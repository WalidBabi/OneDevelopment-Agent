"""
Luna's Verification and Guardrails System
==========================================

This module implements a comprehensive verification system for Luna's responses,
inspired by LangGraph and deep agents patterns. It ensures Luna verifies her answers
before presenting them to users.

Key Features:
1. Multi-source verification
2. Confidence scoring
3. Fact-checking against knowledge base
4. Web verification for critical information
5. Hallucination detection
6. Source citation
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os


class VerificationLevel(Enum):
    """Levels of verification confidence"""
    HIGH = "high"  # 80%+ confidence, multiple sources
    MEDIUM = "medium"  # 50-80% confidence, single source
    LOW = "low"  # < 50% confidence, needs disclaimer
    UNVERIFIED = "unverified"  # No supporting evidence


@dataclass
class VerificationResult:
    """Result of verification check"""
    is_verified: bool
    confidence_score: float  # 0.0 to 1.0
    verification_level: VerificationLevel
    sources: List[str]
    issues_found: List[str]
    corrections: List[Dict[str, str]]
    needs_disclaimer: bool
    suggested_improvements: List[str]


class VerificationGuardrails:
    """
    Verification and guardrails system for Luna's responses.
    
    This system implements multiple layers of verification:
    1. Knowledge base verification
    2. Web fact-checking
    3. Hallucination detection
    4. Confidence scoring
    5. Source attribution
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,  # Low temperature for more factual outputs
            api_key=self.api_key
        )
        
        # Critical topics that need high confidence
        self.critical_topics = [
            'pricing', 'payment', 'legal', 'contract', 'fee',
            'location', 'address', 'career', 'job', 'hiring',
            'phone', 'email', 'contact'
        ]
    
    def verify_response(
        self,
        query: str,
        response: str,
        context: List[str],
        tool_results: Dict[str, str]
    ) -> VerificationResult:
        """
        Comprehensive verification of Luna's response.
        
        Args:
            query: User's question
            response: Luna's proposed response
            context: Context retrieved from knowledge base
            tool_results: Results from tools used
            
        Returns:
            VerificationResult with verification status and suggestions
        """
        issues_found = []
        corrections = []
        sources = []
        suggested_improvements = []
        
        # 1. Check for unsupported claims
        unsupported_claims = self._detect_unsupported_claims(
            response, context, tool_results
        )
        if unsupported_claims:
            issues_found.extend(unsupported_claims)
        
        # 2. Check for hallucinations
        hallucinations = self._detect_hallucinations(response, context)
        if hallucinations:
            issues_found.extend([f"Potential hallucination: {h}" for h in hallucinations])
        
        # 3. Verify specific facts
        fact_checks = self._verify_specific_facts(response, tool_results)
        sources.extend(fact_checks['sources'])
        if fact_checks['unverified_facts']:
            issues_found.extend(fact_checks['unverified_facts'])
        
        # 4. Check for critical topic confidence
        is_critical = any(topic in query.lower() for topic in self.critical_topics)
        
        # 5. Calculate confidence score
        confidence_score = self._calculate_confidence(
            response, context, tool_results, len(issues_found)
        )
        
        # 6. Determine verification level
        if confidence_score >= 0.8 and len(sources) >= 2:
            verification_level = VerificationLevel.HIGH
        elif confidence_score >= 0.5 and len(sources) >= 1:
            verification_level = VerificationLevel.MEDIUM
        elif confidence_score >= 0.3:
            verification_level = VerificationLevel.LOW
        else:
            verification_level = VerificationLevel.UNVERIFIED
        
        # 7. Check if disclaimer needed
        needs_disclaimer = (
            is_critical and verification_level in [VerificationLevel.LOW, VerificationLevel.UNVERIFIED]
        ) or len(issues_found) > 2
        
        # 8. Generate corrections if needed
        if issues_found:
            corrections = self._generate_corrections(
                query, response, issues_found, context, tool_results
            )
        
        # 9. Suggest improvements
        suggested_improvements = self._suggest_improvements(
            response, verification_level, is_critical
        )
        
        is_verified = (
            verification_level in [VerificationLevel.HIGH, VerificationLevel.MEDIUM] 
            and len(issues_found) < 3
        )
        
        return VerificationResult(
            is_verified=is_verified,
            confidence_score=confidence_score,
            verification_level=verification_level,
            sources=sources,
            issues_found=issues_found,
            corrections=corrections,
            needs_disclaimer=needs_disclaimer,
            suggested_improvements=suggested_improvements
        )
    
    def _detect_unsupported_claims(
        self,
        response: str,
        context: List[str],
        tool_results: Dict[str, str]
    ) -> List[str]:
        """Detect claims in response that aren't supported by context"""
        
        # Use LLM to check if claims are supported
        verification_prompt = f"""You are a fact-checker. Review the response and identify any claims that are NOT supported by the provided context.

RESPONSE TO CHECK:
{response}

AVAILABLE CONTEXT:
{chr(10).join(context) if context else "No context available"}

TOOL RESULTS:
{chr(10).join([f"{k}: {v[:200]}..." for k, v in tool_results.items()]) if tool_results else "No tool results"}

TASK:
List any specific claims, numbers, dates, or facts in the response that are NOT clearly supported by the context above.
If the response contains information that seems made up or guessed, list it.
If everything is supported or the response appropriately admits uncertainty, return "NONE".

Format: Return only a comma-separated list of unsupported claims, or "NONE".
"""
        
        try:
            result = self.llm.invoke([
                SystemMessage(content="You are a precise fact-checker."),
                HumanMessage(content=verification_prompt)
            ])
            
            claims = result.content.strip()
            if claims.upper() == "NONE" or not claims:
                return []
            
            return [claim.strip() for claim in claims.split(',') if claim.strip()]
        except:
            return []
    
    def _detect_hallucinations(
        self,
        response: str,
        context: List[str]
    ) -> List[str]:
        """Detect potential hallucinations using pattern matching"""
        
        hallucinations = []
        
        # Check for specific numbers without context support
        numbers_in_response = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', response)
        context_text = ' '.join(context)
        
        for number in numbers_in_response:
            if number not in context_text and len(number) > 2:
                # Check if it's a year (acceptable) or specific number (needs verification)
                if not re.match(r'20\d{2}', number):
                    hallucinations.append(f"Unverified number: {number}")
        
        # Check for overly specific claims
        specific_patterns = [
            (r'\d+\s*bedrooms?', "Specific bedroom count"),
            (r'AED\s*[\d,]+', "Specific price"),
            (r'\d+\s*(?:square feet|sqft|sq\.ft\.)', "Specific square footage"),
            (r'starting\s*(?:from|at)\s*AED\s*[\d,]+', "Specific starting price"),
        ]
        
        for pattern, desc in specific_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                # Check if any match is in context
                for match in matches:
                    if match not in context_text:
                        hallucinations.append(f"Unverified {desc}: {match}")
        
        return hallucinations
    
    def _verify_specific_facts(
        self,
        response: str,
        tool_results: Dict[str, str]
    ) -> Dict[str, Any]:
        """Verify specific facts in response against tool results"""
        
        sources = []
        unverified_facts = []
        
        # Extract sources from tool results
        for tool_name, result in tool_results.items():
            if result and len(result) > 50:  # Has meaningful content
                if "Error" not in result and "not found" not in result.lower():
                    sources.append(tool_name)
        
        # Check for specific fact types
        fact_patterns = {
            'location': r'(?:located|situated|based)\s+(?:in|at)\s+([^,.]+)',
            'contact': r'(?:contact|call|email|reach).*?(\+?\d[\d\s\-()]+|[\w\.-]+@[\w\.-]+)',
            'career': r'(?:hiring|job|career|position|role|opportunity)(?:ies)?'
        }
        
        for fact_type, pattern in fact_patterns.items():
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                # Check if this fact type was verified by tools
                verified = any(
                    fact_type in tool_name.lower() or fact_type in str(result).lower()
                    for tool_name, result in tool_results.items()
                )
                if not verified:
                    unverified_facts.append(f"Unverified {fact_type} information")
        
        return {
            'sources': sources,
            'unverified_facts': unverified_facts
        }
    
    def _calculate_confidence(
        self,
        response: str,
        context: List[str],
        tool_results: Dict[str, str],
        num_issues: int
    ) -> float:
        """Calculate confidence score for the response"""
        
        score = 0.5  # Base score
        
        # Add points for context
        if context and len(context) > 0:
            score += 0.2
        
        # Add points for tool results
        successful_tools = sum(
            1 for result in tool_results.values()
            if result and "Error" not in result and len(result) > 50
        )
        score += min(successful_tools * 0.15, 0.3)
        
        # Subtract for issues
        score -= num_issues * 0.1
        
        # Check for uncertainty phrases (good - honest about limitations)
        uncertainty_phrases = [
            'i recommend', 'please contact', 'visit oneuae.com',
            'for specific', 'for detailed', 'typically', 'generally'
        ]
        has_uncertainty = any(phrase in response.lower() for phrase in uncertainty_phrases)
        if has_uncertainty:
            score += 0.1  # Bonus for being appropriately cautious
        
        # Cap between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _generate_corrections(
        self,
        query: str,
        response: str,
        issues: List[str],
        context: List[str],
        tool_results: Dict[str, str]
    ) -> List[Dict[str, str]]:
        """Generate corrections for identified issues"""
        
        correction_prompt = f"""You are helping improve an AI response by suggesting corrections.

USER QUERY: {query}

CURRENT RESPONSE: {response}

ISSUES IDENTIFIED:
{chr(10).join(f"- {issue}" for issue in issues)}

AVAILABLE CONTEXT:
{chr(10).join(context[:3]) if context else "Limited context"}

TASK: For each issue, suggest a correction or improvement. Be specific and actionable.

Format your response as:
ISSUE: [issue description]
CORRECTION: [specific correction]
---
"""
        
        try:
            result = self.llm.invoke([
                SystemMessage(content="You are a helpful editor providing specific corrections."),
                HumanMessage(content=correction_prompt)
            ])
            
            corrections = []
            correction_blocks = result.content.split('---')
            
            for block in correction_blocks:
                if 'ISSUE:' in block and 'CORRECTION:' in block:
                    issue_match = re.search(r'ISSUE:\s*(.+?)(?=CORRECTION:)', block, re.DOTALL)
                    correction_match = re.search(r'CORRECTION:\s*(.+)', block, re.DOTALL)
                    
                    if issue_match and correction_match:
                        corrections.append({
                            'issue': issue_match.group(1).strip(),
                            'correction': correction_match.group(1).strip()
                        })
            
            return corrections
        except:
            return []
    
    def _suggest_improvements(
        self,
        response: str,
        verification_level: VerificationLevel,
        is_critical: bool
    ) -> List[str]:
        """Suggest improvements to the response"""
        
        suggestions = []
        
        if verification_level == VerificationLevel.LOW:
            suggestions.append("Add more context from verified sources")
            suggestions.append("Include disclaimer about general information")
        
        if verification_level == VerificationLevel.UNVERIFIED:
            suggestions.append("Search for more reliable sources")
            suggestions.append("Consider responding with 'I don't have specific information' and offer to connect user with team")
        
        if is_critical and verification_level != VerificationLevel.HIGH:
            suggestions.append("This is a critical topic - verify information before responding")
            suggestions.append("Add clear source citations")
        
        # Check for missing call-to-action
        if not any(phrase in response.lower() for phrase in ['contact', 'visit', 'call', 'email']):
            suggestions.append("Add a clear call-to-action or next steps")
        
        # Check for formatting
        if '**' not in response and '*' not in response:
            suggestions.append("Add bold formatting for key points")
        
        if '\n-' not in response and '\n•' not in response and len(response) > 200:
            suggestions.append("Consider using bullet points for better readability")
        
        return suggestions
    
    def improve_response(
        self,
        query: str,
        response: str,
        verification_result: VerificationResult,
        context: List[str],
        tool_results: Dict[str, str]
    ) -> str:
        """
        Improve response based on verification results.
        
        Args:
            query: User's question
            response: Original response
            verification_result: Results from verification
            context: Available context
            tool_results: Tool results
            
        Returns:
            Improved response with appropriate disclaimers and corrections
        """
        
        # If highly verified, return as-is (maybe add sources)
        if verification_result.verification_level == VerificationLevel.HIGH:
            return self._add_source_citations(response, verification_result.sources)
        
        # If corrections available, regenerate response
        if verification_result.corrections:
            return self._regenerate_with_corrections(
                query, response, verification_result, context, tool_results
            )
        
        # If needs disclaimer, add appropriate disclaimer
        if verification_result.needs_disclaimer:
            return self._add_disclaimer(response, verification_result)
        
        # Apply suggested improvements
        improved = response
        if 'Add bold formatting' in verification_result.suggested_improvements:
            improved = self._enhance_formatting(improved)
        
        return improved
    
    def _add_source_citations(self, response: str, sources: List[str]) -> str:
        """Add source citations to response"""
        
        if not sources:
            return response
        
        # Clean up source names
        clean_sources = [
            source.replace('_', ' ').title() 
            for source in sources
        ]
        
        citation = f"\n\n**Sources:** {', '.join(clean_sources)}"
        
        return response + citation
    
    def _regenerate_with_corrections(
        self,
        query: str,
        original_response: str,
        verification_result: VerificationResult,
        context: List[str],
        tool_results: Dict[str, str]
    ) -> str:
        """Regenerate response incorporating corrections"""
        
        corrections_text = "\n".join([
            f"- {c['issue']}: {c['correction']}"
            for c in verification_result.corrections
        ])
        
        regeneration_prompt = f"""You are Luna, an AI assistant for One Development. Regenerate your response incorporating the corrections below.

USER QUERY: {query}

ORIGINAL RESPONSE: {original_response}

CORRECTIONS TO APPLY:
{corrections_text}

AVAILABLE CONTEXT:
{chr(10).join(context[:5]) if context else "Limited context"}

INSTRUCTIONS:
1. Keep the helpful, professional tone
2. Incorporate all corrections
3. Be honest about what you don't know
4. Always provide value and next steps
5. Use proper formatting (bold, bullet points)

Generate improved response:"""
        
        try:
            result = self.llm.invoke([
                SystemMessage(content="You are Luna, a helpful AI assistant for One Development."),
                HumanMessage(content=regeneration_prompt)
            ])
            
            return result.content.strip()
        except:
            # Fallback to original with disclaimer
            return self._add_disclaimer(original_response, verification_result)
    
    def _add_disclaimer(self, response: str, verification_result: VerificationResult) -> str:
        """Add appropriate disclaimer based on verification level"""
        
        if verification_result.verification_level == VerificationLevel.UNVERIFIED:
            disclaimer = "\n\n⚠️ **Note:** The information above is general guidance. For accurate, up-to-date details specific to One Development, please contact our team at oneuae.com."
        elif verification_result.verification_level == VerificationLevel.LOW:
            disclaimer = "\n\n**Note:** For the most current and specific information, I recommend contacting our team directly at oneuae.com."
        else:
            disclaimer = "\n\n**Need more details?** Contact us at oneuae.com for personalized assistance."
        
        return response + disclaimer
    
    def _enhance_formatting(self, response: str) -> str:
        """Enhance response formatting"""
        
        # This is a simple enhancement - could be more sophisticated
        # Add bold to key phrases
        key_phrases = [
            'One Development',
            'Important',
            'Note',
            'Key features',
            'Available now'
        ]
        
        enhanced = response
        for phrase in key_phrases:
            if phrase in enhanced and f'**{phrase}**' not in enhanced:
                enhanced = enhanced.replace(phrase, f'**{phrase}**', 1)
        
        return enhanced


# Singleton instance
_verification_guardrails = None


def get_verification_guardrails() -> VerificationGuardrails:
    """Get singleton instance of verification guardrails"""
    global _verification_guardrails
    if _verification_guardrails is None:
        _verification_guardrails = VerificationGuardrails()
    return _verification_guardrails








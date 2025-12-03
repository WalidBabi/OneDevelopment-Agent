from django.core.management.base import BaseCommand
from agent.models import SuggestedQuestion, KnowledgeBase
from agent.data_ingestor import OneDevelopmentDataIngestor
from agent import get_luna_agent


class Command(BaseCommand):
    help = 'Initialize database with suggested questions and initial knowledge'

    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing suggested questions...')
        
        # Clear existing suggested questions
        SuggestedQuestion.objects.all().delete()
        
        # Create suggested questions
        questions = [
            # Company Information
            {'question': 'Tell me about One Development', 'category': 'company_info', 'priority': 10},
            {'question': 'What makes One Development unique?', 'category': 'company_info', 'priority': 9},
            {'question': 'When was One Development established?', 'category': 'company_info', 'priority': 7},
            
            # Projects
            {'question': 'Show me your latest projects', 'category': 'projects', 'priority': 10},
            {'question': 'What properties do you have in Dubai Marina?', 'category': 'projects', 'priority': 8},
            {'question': 'Do you have any ready-to-move properties?', 'category': 'projects', 'priority': 9},
            {'question': 'What are your upcoming developments?', 'category': 'projects', 'priority': 7},
            
            # Services
            {'question': 'What services do you offer?', 'category': 'services', 'priority': 8},
            {'question': 'Do you provide property management?', 'category': 'services', 'priority': 6},
            {'question': 'What is your after-sales support like?', 'category': 'services', 'priority': 6},
            
            # Investment
            {'question': 'What are the investment opportunities?', 'category': 'investment', 'priority': 9},
            {'question': 'What ROI can I expect from your properties?', 'category': 'investment', 'priority': 8},
            {'question': 'Do you offer payment plans?', 'category': 'investment', 'priority': 9},
            {'question': 'Can foreigners buy property through One Development?', 'category': 'investment', 'priority': 7},
            
            # Pricing
            {'question': 'What is the price range of your properties?', 'category': 'pricing', 'priority': 10},
            {'question': 'Are there any current promotions?', 'category': 'pricing', 'priority': 8},
            {'question': 'What are the payment options available?', 'category': 'pricing', 'priority': 9},
            
            # Amenities
            {'question': 'What amenities are included in your properties?', 'category': 'amenities', 'priority': 8},
            {'question': 'Do your properties have swimming pools?', 'category': 'amenities', 'priority': 6},
            {'question': 'Is parking included?', 'category': 'amenities', 'priority': 5},
            
            # Location
            {'question': 'Where are your properties located?', 'category': 'location', 'priority': 9},
            {'question': 'Are your offices in Dubai?', 'category': 'location', 'priority': 7},
            {'question': 'Which areas of Dubai do you focus on?', 'category': 'location', 'priority': 8},
            
            # Contact
            {'question': 'How can I contact you?', 'category': 'contact', 'priority': 8},
            {'question': 'Can I schedule a property viewing?', 'category': 'contact', 'priority': 9},
            {'question': 'What are your office hours?', 'category': 'contact', 'priority': 5},
            
            # Career
            {'question': 'Are you hiring?', 'category': 'career', 'priority': 7},
            {'question': 'What career opportunities are available?', 'category': 'career', 'priority': 7},
            {'question': 'How can I apply for a job?', 'category': 'career', 'priority': 6},
        ]
        
        for q_data in questions:
            SuggestedQuestion.objects.create(**q_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(questions)} suggested questions'))
        
        # Initialize knowledge base
        self.stdout.write('Initializing knowledge base...')
        
        ingestor = OneDevelopmentDataIngestor()
        initial_data = ingestor.get_initial_knowledge()
        
        # Clear existing knowledge base
        KnowledgeBase.objects.all().delete()
        
        # Create knowledge base entries
        for item in initial_data:
            KnowledgeBase.objects.create(
                source_type=item.get('source_type', 'manual'),
                title=item.get('title', 'Untitled'),
                content=item.get('content', ''),
                summary=item.get('content', '')[:500],
                metadata={'category': item.get('category', 'general')}
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(initial_data)} knowledge base entries'))
        
        # Initialize vector store using Luna DeepAgent
        self.stdout.write('Initializing vector store with Luna DeepAgent...')
        try:
            agent = get_luna_agent()
            for item in initial_data:
                agent.add_knowledge(
                    content=item.get('content', ''),
                    metadata={
                        'source': item.get('source_type'),
                        'title': item.get('title'),
                        'category': item.get('category', 'general')
                    }
                )
            self.stdout.write(self.style.SUCCESS('Vector store initialized'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not initialize vector store: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Data initialization complete!'))


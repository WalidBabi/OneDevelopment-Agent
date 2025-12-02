"""
Management command to bulk ingest PDFs from a folder or download from URLs.
Also includes curated project data for known One Development properties.
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from agent.models import PDFDocument, KnowledgeBase
from agent.pdf_processor import PDFProcessor
from knowledge.vector_store import get_vector_store
import os
import requests
import time


class Command(BaseCommand):
    help = 'Bulk ingest PDFs from folder, URLs, or add curated project data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            type=str,
            help='Path to folder containing PDF files to ingest'
        )
        parser.add_argument(
            '--url',
            type=str,
            help='URL of a PDF to download and ingest'
        )
        parser.add_argument(
            '--add-projects',
            action='store_true',
            help='Add curated data about known One Development projects'
        )

    def handle(self, *args, **options):
        processor = PDFProcessor()
        vector_store = get_vector_store()
        
        if options['folder']:
            self.ingest_folder(options['folder'], processor)
        
        if options['url']:
            self.ingest_from_url(options['url'], processor)
        
        if options['add_projects']:
            self.add_project_data(vector_store)
        
        if not any([options['folder'], options['url'], options['add_projects']]):
            self.stdout.write(self.style.WARNING(
                'No action specified. Use --folder, --url, or --add-projects'
            ))
            self.stdout.write('\nExamples:')
            self.stdout.write('  python manage.py ingest_pdfs --folder=/path/to/pdfs')
            self.stdout.write('  python manage.py ingest_pdfs --url=https://example.com/brochure.pdf')
            self.stdout.write('  python manage.py ingest_pdfs --add-projects')

    def ingest_folder(self, folder_path, processor):
        """Ingest all PDFs from a folder"""
        self.stdout.write(f'\n📁 Ingesting PDFs from: {folder_path}')
        
        if not os.path.exists(folder_path):
            self.stdout.write(self.style.ERROR(f'Folder not found: {folder_path}'))
            return
        
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            self.stdout.write(self.style.WARNING('No PDF files found in folder'))
            return
        
        count = 0
        for pdf_file in pdf_files:
            pdf_path = os.path.join(folder_path, pdf_file)
            try:
                # Create PDFDocument
                with open(pdf_path, 'rb') as f:
                    pdf_doc = PDFDocument.objects.create(
                        title=pdf_file.replace('.pdf', '').replace('_', ' ').replace('-', ' '),
                        description=f'Imported from {pdf_file}',
                        is_active=True
                    )
                    pdf_doc.file.save(pdf_file, ContentFile(f.read()))
                
                # Process and index
                processor.process_and_index_pdf(pdf_doc)
                count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Indexed: {pdf_file}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error with {pdf_file}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Ingested {count} PDFs'))

    def ingest_from_url(self, url, processor):
        """Download and ingest PDF from URL"""
        self.stdout.write(f'\n🌐 Downloading PDF from: {url}')
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Get filename from URL or headers
            filename = url.split('/')[-1]
            if not filename.endswith('.pdf'):
                filename = 'downloaded_brochure.pdf'
            
            # Create PDFDocument
            pdf_doc = PDFDocument.objects.create(
                title=filename.replace('.pdf', '').replace('_', ' ').replace('-', ' '),
                description=f'Downloaded from {url}',
                is_active=True
            )
            pdf_doc.file.save(filename, ContentFile(response.content))
            
            # Process and index
            processor.process_and_index_pdf(pdf_doc)
            self.stdout.write(self.style.SUCCESS(f'✅ Downloaded and indexed: {filename}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))

    def add_project_data(self, vector_store):
        """Add curated data about One Development projects"""
        self.stdout.write('\n🏗️ Adding curated project data...')
        
        projects = [
            # ============================================================
            # LAGUNA RESIDENCE
            # ============================================================
            {
                'title': 'Laguna Residence - Project Overview',
                'content': '''
**Laguna Residence by One Development**

Laguna Residence is a premium residential development by One Development, located in a prime area of Dubai.

**Project Highlights:**
• Modern architectural design with contemporary finishes
• Range of unit types from studios to spacious apartments
• World-class amenities and facilities
• Strategic location with excellent connectivity
• Attractive payment plans available

**Key Features:**
• Swimming pool and fitness center
• 24/7 security and concierge
• Landscaped gardens and common areas
• Dedicated parking facilities
• Smart home features

**Location Benefits:**
• Close to major highways and metro stations
• Near shopping malls and retail centers
• Access to schools and healthcare facilities
• Minutes from Dubai's key business districts

**Investment Potential:**
• High rental yield potential
• Strong capital appreciation prospects
• Freehold ownership for all nationalities
• Golden Visa eligible (subject to value)

For detailed information, floor plans, and pricing, contact One Development sales team at oneuae.com.
                ''',
                'category': 'projects',
                'project_name': 'Laguna Residence'
            },
            
            # ============================================================
            # ONE DEVELOPMENT PROJECTS OVERVIEW
            # ============================================================
            {
                'title': 'One Development Projects Portfolio',
                'content': '''
**One Development Project Portfolio**

One Development has a growing portfolio of premium residential and commercial developments in Dubai and the UAE.

**Active Projects:**
• Laguna Residence - Premium residential development
• Additional projects in prime Dubai locations

**Project Standards:**
All One Development projects feature:
• Premium quality construction
• Modern architectural designs
• High-end finishes and fixtures
• Comprehensive amenities
• Strategic locations

**Typical Unit Types:**
• Studios (400-600 sq ft)
• 1 Bedroom (700-1000 sq ft)
• 2 Bedroom (1100-1500 sq ft)
• 3 Bedroom (1600-2200 sq ft)
• Penthouses and duplexes available in select projects

**Standard Amenities:**
• Swimming pools (temperature-controlled)
• Fully-equipped gyms
• Children's play areas
• BBQ and entertainment areas
• Parking facilities
• 24/7 security

**Payment Plans:**
• Flexible payment structures
• Post-handover options available
• Construction-linked payments

Visit oneuae.com for current project listings and availability.
                ''',
                'category': 'projects',
                'project_name': 'Portfolio Overview'
            },
            
            # ============================================================
            # BROCHURE DOWNLOAD INFORMATION
            # ============================================================
            {
                'title': 'Download Project Brochures',
                'content': '''
**One Development Brochures and Information**

Detailed project brochures are available for all One Development properties.

**What's in Our Brochures:**
• Project overview and concept
• Floor plans and layouts
• Unit specifications
• Amenity details
• Location maps
• Payment plan options
• Developer information

**How to Get Brochures:**
1. Visit the project page on oneuae.com
2. Click "Download Brochure" button
3. Fill in your details
4. Receive brochure via email or download directly

**Available Brochures:**
• Laguna Residence Brochure
• Company Profile
• Project Fact Sheets

**Request Information:**
For personalized presentations and brochures, contact our sales team who can:
• Send detailed digital brochures
• Arrange virtual or in-person presentations
• Provide customized information packages
• Schedule site visits

Contact: Visit oneuae.com or reach out to our sales team.
                ''',
                'category': 'brochures',
                'project_name': 'General'
            },
            
            # ============================================================
            # FLOOR PLANS AND UNIT TYPES
            # ============================================================
            {
                'title': 'Floor Plans and Unit Types',
                'content': '''
**One Development Floor Plans and Unit Types**

One Development offers diverse unit configurations to suit various lifestyle needs.

**Studio Units:**
• Size: Typically 400-600 sq ft
• Layout: Open plan living/bedroom
• Features: Kitchen, bathroom, balcony
• Ideal for: Singles, young professionals, investors

**1 Bedroom Units:**
• Size: Typically 700-1000 sq ft
• Layout: Separate bedroom, living room
• Features: Kitchen, 1-2 bathrooms, balcony
• Ideal for: Singles, couples, first-time buyers

**2 Bedroom Units:**
• Size: Typically 1100-1500 sq ft
• Layout: Master + second bedroom
• Features: Kitchen, 2-3 bathrooms, living/dining
• Ideal for: Small families, those needing home office

**3 Bedroom Units:**
• Size: Typically 1600-2200 sq ft
• Layout: Master + 2 bedrooms
• Features: Maid's room option, multiple bathrooms
• Ideal for: Growing families, those wanting space

**Premium Units:**
• Penthouses with private terraces
• Duplex apartments
• Garden units with private outdoor space

For specific floor plans and availability, contact our sales team at oneuae.com.
                ''',
                'category': 'floor_plans',
                'project_name': 'General'
            },
        ]
        
        count = 0
        for project in projects:
            try:
                kb_entry, created = KnowledgeBase.objects.get_or_create(
                    title=project['title'],
                    defaults={
                        'content': project['content'].strip(),
                        'summary': project['content'][:500].strip(),
                        'source_type': 'curated',
                        'metadata': {
                            'category': project['category'],
                            'project': project['project_name']
                        },
                        'is_active': True
                    }
                )
                
                if created:
                    vector_store.add_texts(
                        texts=[project['content'].strip()],
                        metadatas=[{
                            'title': project['title'],
                            'category': project['category'],
                            'project': project['project_name']
                        }]
                    )
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✅ Added: {project['title']}"))
                else:
                    self.stdout.write(f"  ⏭️  Already exists: {project['title']}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Added {count} project entries'))


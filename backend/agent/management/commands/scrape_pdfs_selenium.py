"""
Selenium-based PDF scraper for Cloudflare-protected websites.
This command uses Selenium with Chrome to bypass protection and download PDFs.

Usage:
    python manage.py scrape_pdfs_selenium --project="Laguna Residence"
    python manage.py scrape_pdfs_selenium --all-projects
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from agent.models import PDFDocument, KnowledgeBase
from agent.pdf_processor import PDFProcessor
from knowledge.vector_store import get_vector_store
import os
import time
import re


class Command(BaseCommand):
    help = 'Scrape PDFs from One Development website using Selenium'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project',
            type=str,
            help='Project name to scrape (e.g., "Laguna Residence")'
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            help='Scrape all known projects'
        )
        parser.add_argument(
            '--list-projects',
            action='store_true',
            help='List all project URLs that will be scraped'
        )
        parser.add_argument(
            '--scrape-content',
            action='store_true',
            help='Scrape page content (not PDFs) and store in knowledge base'
        )

    def handle(self, *args, **options):
        # Known project URLs
        self.project_urls = {
            'Laguna Residence': 'https://www.oneuae.com/development-detail?title=Laguna%20Residence',
            # Add more projects as they become known
        }
        
        if options['list_projects']:
            self.list_projects()
            return
        
        if options['scrape_content']:
            if options['project']:
                self.scrape_project_content(options['project'])
            elif options['all_projects']:
                for project in self.project_urls.keys():
                    self.scrape_project_content(project)
            else:
                self.stdout.write(self.style.WARNING(
                    'Specify --project="Name" or --all-projects with --scrape-content'
                ))
            return
        
        if options['project']:
            self.scrape_project(options['project'])
        elif options['all_projects']:
            for project in self.project_urls.keys():
                self.scrape_project(project)
        else:
            self.stdout.write(self.style.WARNING(
                'No action specified. Use:'
            ))
            self.stdout.write('  --project="Laguna Residence" - Scrape specific project')
            self.stdout.write('  --all-projects - Scrape all known projects')
            self.stdout.write('  --list-projects - List available projects')
            self.stdout.write('  --scrape-content - Scrape page content (not PDFs)')
            self.stdout.write('\nAlternative: Use the PDF Admin Dashboard')
            self.stdout.write('  URL: http://your-domain/pdf-admin/')
            self.stdout.write('  Manually download PDFs and upload them there.')

    def list_projects(self):
        """List all known project URLs"""
        self.stdout.write('\n📋 Known One Development Projects:\n')
        for name, url in self.project_urls.items():
            self.stdout.write(f'  • {name}')
            self.stdout.write(f'    URL: {url}\n')

    def scrape_project(self, project_name):
        """Scrape PDF from a specific project page"""
        if project_name not in self.project_urls:
            self.stdout.write(self.style.ERROR(
                f'Unknown project: {project_name}'
            ))
            self.stdout.write('Known projects: ' + ', '.join(self.project_urls.keys()))
            return
        
        url = self.project_urls[project_name]
        self.stdout.write(f'\n🌐 Scraping: {project_name}')
        self.stdout.write(f'   URL: {url}')
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Set download preferences
            download_dir = '/tmp/pdf_downloads'
            os.makedirs(download_dir, exist_ok=True)
            
            prefs = {
                'download.default_directory': download_dir,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'plugins.always_open_pdf_externally': True
            }
            chrome_options.add_experimental_option('prefs', prefs)
            
            self.stdout.write('   Starting Chrome...')
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                self.stdout.write('   Loading page...')
                driver.get(url)
                
                # Wait for Cloudflare challenge to complete
                self.stdout.write('   Waiting for page load...')
                time.sleep(10)  # Wait for Cloudflare
                
                # Wait for the page to fully load
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
                
                # Extract page content first
                self.stdout.write('   Extracting page content...')
                page_content = self.extract_page_content(driver, project_name)
                
                if page_content:
                    self.save_content_to_kb(project_name, page_content)
                
                # Look for PDF download buttons/links
                self.stdout.write('   Looking for PDF links...')
                pdf_links = self.find_pdf_links(driver)
                
                if pdf_links:
                    for link in pdf_links:
                        self.stdout.write(f'   Found PDF: {link}')
                        self.download_and_save_pdf(link, project_name, driver)
                else:
                    self.stdout.write(self.style.WARNING(
                        '   No direct PDF links found. Try the PDF Admin Dashboard.'
                    ))
                
            finally:
                driver.quit()
                
        except ImportError:
            self.stdout.write(self.style.ERROR(
                '❌ Selenium not available. Install with: pip install selenium'
            ))
            self.provide_manual_instructions(project_name)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            self.provide_manual_instructions(project_name)

    def scrape_project_content(self, project_name):
        """Scrape just the page content (text) without PDFs"""
        if project_name not in self.project_urls:
            self.stdout.write(self.style.ERROR(f'Unknown project: {project_name}'))
            return
            
        url = self.project_urls[project_name]
        self.stdout.write(f'\n📄 Scraping content for: {project_name}')
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get(url)
                time.sleep(10)  # Wait for Cloudflare
                
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
                
                content = self.extract_page_content(driver, project_name)
                
                if content:
                    self.save_content_to_kb(project_name, content)
                    self.stdout.write(self.style.SUCCESS(f'✅ Saved content for {project_name}'))
                else:
                    self.stdout.write(self.style.WARNING('No content extracted'))
                    
            finally:
                driver.quit()
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))

    def extract_page_content(self, driver, project_name):
        """Extract text content from the page"""
        try:
            from selenium.webdriver.common.by import By
            
            # Remove unwanted elements
            driver.execute_script("""
                var elements = document.querySelectorAll('script, style, nav, footer, header, iframe');
                elements.forEach(function(el) { el.remove(); });
            """)
            
            # Get main content
            body = driver.find_element(By.TAG_NAME, 'body')
            text = body.text
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned = '\n'.join(lines)
            
            return cleaned if len(cleaned) > 100 else None
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   Content extraction error: {str(e)}'))
            return None

    def save_content_to_kb(self, project_name, content):
        """Save scraped content to knowledge base"""
        vector_store = get_vector_store()
        
        try:
            kb_entry, created = KnowledgeBase.objects.update_or_create(
                title=f'{project_name} - Scraped Content',
                defaults={
                    'content': content[:10000],  # Limit size
                    'summary': content[:500],
                    'source_type': 'website_scrape',
                    'source_url': self.project_urls.get(project_name),
                    'metadata': {'project': project_name, 'method': 'selenium'},
                    'is_active': True
                }
            )
            
            # Add to vector store
            vector_store.add_texts(
                texts=[content[:5000]],
                metadatas=[{'title': project_name, 'source': 'website_scrape'}]
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   Error saving to KB: {str(e)}'))

    def find_pdf_links(self, driver):
        """Find PDF download links on the page"""
        from selenium.webdriver.common.by import By
        
        pdf_links = []
        
        # Look for direct PDF links
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            href = link.get_attribute('href') or ''
            text = link.text.lower()
            
            if '.pdf' in href.lower():
                pdf_links.append(href)
            elif any(word in text for word in ['download', 'brochure', 'pdf', 'fact sheet']):
                if href:
                    pdf_links.append(href)
        
        # Look for download buttons
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button, .btn, [role="button"]')
        for btn in buttons:
            text = btn.text.lower()
            onclick = btn.get_attribute('onclick') or ''
            
            if any(word in text for word in ['download', 'brochure']):
                if '.pdf' in onclick:
                    # Extract PDF URL from onclick
                    match = re.search(r'https?://[^\s\'"]+\.pdf', onclick)
                    if match:
                        pdf_links.append(match.group())
        
        return list(set(pdf_links))  # Remove duplicates

    def download_and_save_pdf(self, url, project_name, driver):
        """Download PDF and save to database"""
        try:
            import requests
            
            # Get cookies from Selenium session
            cookies = {c['name']: c['value'] for c in driver.get_cookies()}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': self.project_urls.get(project_name, 'https://www.oneuae.com')
            }
            
            response = requests.get(url, headers=headers, cookies=cookies, timeout=30)
            response.raise_for_status()
            
            # Determine filename
            filename = url.split('/')[-1]
            if not filename.endswith('.pdf'):
                filename = f'{project_name.replace(" ", "_")}_brochure.pdf'
            
            # Save to database
            pdf_doc = PDFDocument.objects.create(
                title=f'{project_name} Brochure',
                description=f'Downloaded from {url}',
                is_active=True
            )
            pdf_doc.file.save(filename, ContentFile(response.content))
            
            # Index the PDF
            processor = PDFProcessor()
            processor.process_and_index_pdf(pdf_doc)
            
            self.stdout.write(self.style.SUCCESS(f'   ✅ Downloaded and indexed: {filename}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Download error: {str(e)}'))

    def provide_manual_instructions(self, project_name):
        """Provide manual instructions when automated scraping fails"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.WARNING('📋 MANUAL DOWNLOAD INSTRUCTIONS'))
        self.stdout.write('='*60)
        self.stdout.write(f'''
Since automated scraping encountered issues, please manually download the PDF:

1. Open your browser and go to:
   {self.project_urls.get(project_name, 'https://www.oneuae.com')}

2. Click the "Download Brochure" button on the page

3. Save the PDF file to your computer

4. Upload it using one of these methods:

   **Option A: PDF Admin Dashboard (Recommended)**
   - Go to: http://your-domain/pdf-admin/
   - Drag and drop the PDF file
   - It will be automatically indexed

   **Option B: Django Admin**
   - Go to: http://your-domain/admin/agent/pdfdocument/
   - Click "Add PDF Document"
   - Upload the file and save

   **Option C: Command Line**
   - Copy PDF to server: /path/to/pdfs/
   - Run: python manage.py ingest_pdfs --folder=/path/to/pdfs/

The PDF content will be extracted and indexed into Luna's knowledge base.
''')
        self.stdout.write('='*60)


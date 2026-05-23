#!/usr/bin/env python3
"""
RecordsReveal Master Investigation Builder
===========================================

ONE COMMAND to go from CSV → Published Investigation

Runs the complete automation pipeline:
1. analyze_v2.py - Data analysis + visualizations
2. generate_article.py - Extract findings
3. ai_writer.py - Generate journalism prose
4. build_investigation_html.py - Build complete HTML
5. update_homepage.py - Add to index.html

Usage:
    python3 build_investigation.py dataset.csv "TARGET_COLUMN" \\
        --name "Investigation Name" \\
        --inv-number 004 \\
        --category "Crime" \\
        --emoji "🚔" \\
        --label "CRIME DATA" \\
        --theme-color "#8b4513" \\
        --output-filename "fbi-crime.html"

Example:
    python3 build_investigation.py fbi_crime.csv "violent_crime_rate" \\
        --name "FBI Crime Data" \\
        --inv-number 004 \\
        --category "FBI Crime Analysis" \\
        --emoji "🚔" \\
        --label "CRIME DATA"

Author: RecordsReveal Data Team
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import shutil


class InvestigationBuilder:
    """Orchestrates the complete investigation building pipeline"""
    
    def __init__(self, csv_path, target_col, config):
        self.csv_path = Path(csv_path)
        self.target_col = target_col
        self.config = config
        self.results = {}
        
        # Setup paths
        self.work_dir = self.csv_path.parent / 'analysis_results'
        self.results_json = self.work_dir / 'results.json'
        self.article_json = self.work_dir / 'article_content.json'
        self.full_article_json = self.work_dir / 'full_article.json'
        self.viz_dir = self.work_dir / 'visualizations'
        
    def run_step(self, step_name, command, description):
        """Run a pipeline step and handle errors"""
        print("\n" + "=" * 60)
        print(f"STEP: {step_name}")
        print("=" * 60)
        print(f"📝 {description}")
        print(f"🔧 Command: {' '.join(command)}")
        print()
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=False,
                text=True
            )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"\n✅ {step_name} completed in {elapsed:.1f}s")
            return True
            
        except subprocess.CalledProcessError as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"\n❌ {step_name} failed after {elapsed:.1f}s")
            print(f"   Error code: {e.returncode}")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error in {step_name}: {e}")
            return False
    
    def step1_analyze(self):
        """Run data analysis"""
        command = [
            'python3',
            'analyze_v2.py',
            str(self.csv_path),
            self.target_col
        ]
        
        return self.run_step(
            "1/5: DATA ANALYSIS",
            command,
            "Running ML analysis, generating visualizations..."
        )
    
    def step2_generate_article(self):
        """Generate article structure"""
        command = [
            'python3',
            'generate_article.py',
            str(self.results_json)
        ]
        
        return self.run_step(
            "2/5: ARTICLE GENERATION",
            command,
            "Extracting findings and creating article structure..."
        )
    
    def step3_ai_writer(self):
        """Generate AI prose"""
        command = [
            'python3',
            'ai_writer.py',
            str(self.article_json),
            str(self.results_json),
            '--dataset-name',
            self.config['name']
        ]
        
        return self.run_step(
            "3/5: AI WRITING",
            command,
            f"Generating journalism prose for '{self.config['name']}'..."
        )
    
    def step4_build_html(self):
        """Build HTML investigation page"""
        output_filename = self.config.get('output_filename', f"investigation-{self.config['inv_number']}.html")
        output_path = Path('investigations') / output_filename
        
        command = [
            'python3',
            'build_investigation_html.py',
            str(self.full_article_json),
            str(self.viz_dir),
            '--output',
            str(output_path),
            '--investigation-number',
            self.config['inv_number'],
            '--category',
            self.config['category'],
            '--theme-color',
            self.config.get('theme_color', '#d2691e')
        ]
        
        success = self.run_step(
            "4/5: HTML GENERATION",
            command,
            f"Building complete HTML page..."
        )
        
        if success:
            self.results['html_path'] = output_path
            
        return success
    
    def step5_update_homepage(self):
        """Add investigation to homepage"""
        command = [
            'python3',
            'update_homepage.py',
            str(self.full_article_json),
            '--inv-number',
            self.config['inv_number'],
            '--category',
            self.config['category'],
            '--emoji',
            self.config.get('emoji', '📊'),
            '--label',
            self.config.get('label', 'DATA'),
            '--filename',
            self.config.get('output_filename', f"investigation-{self.config['inv_number']}.html")
        ]
        
        return self.run_step(
            "5/5: HOMEPAGE UPDATE",
            command,
            "Adding investigation card to index.html..."
        )
    
    def run_pipeline(self):
        """Execute complete pipeline"""
        print("\n" + "=" * 60)
        print("🚀 RECORDSREVEAL INVESTIGATION BUILDER")
        print("=" * 60)
        print(f"\n📊 Dataset: {self.csv_path.name}")
        print(f"🎯 Target: {self.target_col}")
        print(f"📰 Name: {self.config['name']}")
        print(f"🏷️  Category: {self.config['category']}")
        print(f"🔢 Investigation #: {self.config['inv_number']}")
        
        start_time = datetime.now()
        
        # Step 1: Analyze data
        if not self.step1_analyze():
            return self.abort("Data analysis failed")
        
        if not self.results_json.exists():
            return self.abort(f"Expected output not found: {self.results_json}")
        
        # Step 2: Generate article structure
        if not self.step2_generate_article():
            return self.abort("Article generation failed")
        
        if not self.article_json.exists():
            return self.abort(f"Expected output not found: {self.article_json}")
        
        # Step 3: AI writing
        if not self.step3_ai_writer():
            return self.abort("AI writing failed")
        
        if not self.full_article_json.exists():
            return self.abort(f"Expected output not found: {self.full_article_json}")
        
        # Step 4: Build HTML
        if not self.step4_build_html():
            return self.abort("HTML generation failed")
        
        # Step 5: Update homepage
        if not self.step5_update_homepage():
            print("\n⚠️  Homepage update failed, but investigation HTML is complete")
            print(f"   You can manually add it to index.html")
        
        # Success!
        total_time = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("✅ INVESTIGATION BUILD COMPLETE!")
        print("=" * 60)
        print(f"\n⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        print(f"\n📁 Generated files:")
        print(f"   📊 Analysis: {self.results_json}")
        print(f"   📝 Article: {self.full_article_json}")
        print(f"   🎨 Visualizations: {self.viz_dir}/")
        print(f"   🌐 HTML: {self.results.get('html_path', 'N/A')}")
        print(f"   🏠 Homepage: index.html (updated)")
        
        print(f"\n🎉 Your investigation is ready to publish!")
        print(f"\n🌐 View it:")
        print(f"   open {self.results.get('html_path', 'investigations/')}")
        
        return True
    
    def abort(self, reason):
        """Abort pipeline with error message"""
        print("\n" + "=" * 60)
        print("❌ PIPELINE ABORTED")
        print("=" * 60)
        print(f"\n💥 Reason: {reason}")
        print(f"\n📁 Partial results may be in: {self.work_dir}")
        return False


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    csv_path = sys.argv[1]
    target_col = sys.argv[2]
    
    # Parse configuration
    config = {
        'name': 'Data Investigation',
        'inv_number': '004',
        'category': 'Data Analysis',
        'emoji': '📊',
        'label': 'DATA',
        'theme_color': '#d2691e',
        'output_filename': None
    }
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--name' and i + 1 < len(sys.argv):
            config['name'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--inv-number' and i + 1 < len(sys.argv):
            config['inv_number'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--category' and i + 1 < len(sys.argv):
            config['category'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--emoji' and i + 1 < len(sys.argv):
            config['emoji'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--label' and i + 1 < len(sys.argv):
            config['label'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--theme-color' and i + 1 < len(sys.argv):
            config['theme_color'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output-filename' and i + 1 < len(sys.argv):
            config['output_filename'] = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Auto-generate output filename if not provided
    if not config['output_filename']:
        config['output_filename'] = f"investigation-{config['inv_number']}.html"
    
    # Build investigation
    builder = InvestigationBuilder(csv_path, target_col, config)
    success = builder.run_pipeline()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

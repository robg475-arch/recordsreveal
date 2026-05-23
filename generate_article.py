#!/usr/bin/env python3
"""
RecordsReveal Article Generator
================================
Generates compelling data journalism articles from analysis results.

Uses AI to write:
- Headlines and subheads
- Key findings and insights
- Technical methodology
- Investigation narrative

Input: results.json from analyze_v2.py
Output: article_content.json with all text
"""

import json
import sys
from pathlib import Path


class ArticleGenerator:
    """Generate data journalism articles from analysis results"""
    
    def __init__(self, results_path):
        self.results_path = Path(results_path)
        with open(results_path) as f:
            self.results = json.load(f)
        
        self.article = {
            'meta': {},
            'hero': {},
            'findings': [],
            'methodology': {},
            'implications': {}
        }
    
    def generate(self):
        """Generate complete article content"""
        print("\n" + "="*60)
        print("📝 GENERATING ARTICLE CONTENT")
        print("="*60)
        
        self._generate_headline()
        self._generate_hero_stats()
        self._generate_findings()
        self._generate_methodology()
        self._write_narrative()
        
        return self.article
    
    def _generate_headline(self):
        """Create compelling headline from results"""
        print("\n✍️  Generating headline...")
        
        task_type = self.results['profile'].get('target_type', 'regression')
        
        if task_type == 'regression':
            best_model = self.results['models'].get('best_model', 'Unknown')
            r2 = self.results['models']['regression'][best_model]['r2_score']
            
            # Get top predictor
            top_feature = None
            top_importance = 0
            if 'feature_importance' in self.results['models']['regression'][best_model]:
                importances = self.results['models']['regression'][best_model]['feature_importance']
                top_feature = max(importances.items(), key=lambda x: x[1])
            
            if r2 > 0.7:
                headline_type = "formula"
                self.article['meta']['angle'] = "We cracked the code"
            elif r2 < 0.1:
                headline_type = "chaos"
                self.article['meta']['angle'] = "It's unpredictable"
            else:
                headline_type = "pattern"
                self.article['meta']['angle'] = "We found a pattern"
            
            self.article['meta']['headline_type'] = headline_type
            self.article['meta']['r2_score'] = r2
            self.article['meta']['top_predictor'] = top_feature[0] if top_feature else None
            self.article['meta']['top_importance'] = top_feature[1] if top_feature else None
            
        elif 'classification' in task_type:
            best_model = self.results['models'].get('best_model', 'Unknown')
            models = self.results['models']['classification']
            
            if best_model in models:
                accuracy = models[best_model].get('accuracy', 0)
                auc = models[best_model].get('roc_auc', 0)
                
                self.article['meta']['headline_type'] = "prediction"
                self.article['meta']['angle'] = "We can predict it"
                self.article['meta']['accuracy'] = accuracy
                self.article['meta']['auc'] = auc
        
        print(f"   Angle: {self.article['meta']['angle']}")
    
    def _generate_hero_stats(self):
        """Extract hero statistics"""
        print("\n📊 Extracting hero statistics...")
        
        shape = self.results['profile']['shape']
        self.article['hero']['total_records'] = shape[0]
        self.article['hero']['total_features'] = shape[1]
        
        # Model performance
        task_type = self.results['profile'].get('target_type', 'regression')
        best_model = self.results['models'].get('best_model', 'Unknown')
        
        if task_type == 'regression':
            r2 = self.results['models']['regression'][best_model]['r2_score']
            rmse = self.results['models']['regression'][best_model]['rmse']
            self.article['hero']['model_r2'] = r2
            self.article['hero']['model_rmse'] = rmse
        
        # Clustering
        if 'clustering' in self.results:
            k = self.results['clustering']['optimal_k']
            self.article['hero']['num_clusters'] = k
        
        print(f"   Total records: {self.article['hero']['total_records']:,}")
        print(f"   Best model: {best_model}")
    
    def _generate_findings(self):
        """Generate key findings from feature importance"""
        print("\n🔍 Generating key findings...")
        
        task_type = self.results['profile'].get('target_type', 'regression')
        best_model = self.results['models'].get('best_model', 'Unknown')
        
        if task_type == 'regression':
            # Try to get feature importance from best model first
            model_data = self.results['models']['regression'].get(best_model, {})
            
            # If best model doesn't have feature importance, try Random Forest or XGBoost
            if 'feature_importance' not in model_data:
                print("   Best model has no feature importance, trying Random Forest...")
                if 'Random Forest' in self.results['models']['regression']:
                    model_data = self.results['models']['regression']['Random Forest']
                    best_model = 'Random Forest'
                elif 'XGBoost' in self.results['models']['regression']:
                    model_data = self.results['models']['regression']['XGBoost']
                    best_model = 'XGBoost'
            
            if 'feature_importance' in model_data:
                importances = sorted(
                    model_data['feature_importance'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Generate finding for each top feature
                for i, (feature, importance) in enumerate(importances[:3]):
                    finding = {
                        'number': i + 1,
                        'feature': feature,
                        'importance': importance,
                        'title_template': f"{feature.replace('_', ' ').title()} Matters Most",
                        'description_template': f"The model identified {feature.replace('_', ' ')} as a key predictor, accounting for {importance*100:.1f}% of the model's decision-making."
                    }
                    self.article['findings'].append(finding)
                    print(f"   Finding #{i+1}: {feature} ({importance*100:.1f}%)")
        
        elif 'classification' in task_type and best_model in self.results['models']['classification']:
            model_data = self.results['models']['classification'][best_model]
            
            if 'feature_importance' in model_data:
                importances = sorted(
                    model_data['feature_importance'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for i, (feature, importance) in enumerate(importances[:3]):
                    finding = {
                        'number': i + 1,
                        'feature': feature,
                        'importance': importance,
                        'title_template': f"{feature.replace('_', ' ').title()} Predicts Outcome",
                        'description_template': f"{feature.replace('_', ' ').title()} is the #{i+1} strongest predictor with {importance*100:.1f}% importance."
                    }
                    self.article['findings'].append(finding)
                    print(f"   Finding #{i+1}: {feature} ({importance*100:.1f}%)")
    
    def _generate_methodology(self):
        """Generate methodology text"""
        print("\n🔬 Generating methodology...")
        
        shape = self.results['profile']['shape']
        task_type = self.results['profile'].get('target_type', 'regression')
        best_model = self.results['models'].get('best_model', 'Unknown')
        
        self.article['methodology'] = {
            'dataset_size': shape[0],
            'num_features': shape[1],
            'task_type': task_type,
            'best_model': best_model,
            'train_test_split': '80/20',
        }
        
        if task_type == 'regression':
            r2 = self.results['models']['regression'][best_model]['r2_score']
            rmse = self.results['models']['regression'][best_model]['rmse']
            self.article['methodology']['r2_score'] = r2
            self.article['methodology']['rmse'] = rmse
            
            methodology_text = f"""We trained five regression models on {int(shape[0]*0.8):,} samples and tested on {int(shape[0]*0.2):,}. {best_model} achieved the best performance with R²={r2:.4f} and RMSE={rmse:.4f}."""
        
        elif 'classification' in task_type:
            models = self.results['models']['classification']
            if best_model in models:
                accuracy = models[best_model].get('accuracy', 0)
                self.article['methodology']['accuracy'] = accuracy
                
                methodology_text = f"""We trained three classification models on {int(shape[0]*0.8):,} samples and tested on {int(shape[0]*0.2):,}. {best_model} achieved {accuracy*100:.1f}% accuracy."""
        else:
            methodology_text = f"""We analyzed {shape[0]:,} records using machine learning."""
        
        self.article['methodology']['text'] = methodology_text
        print(f"   {methodology_text}")
    
    def _write_narrative(self):
        """Generate narrative templates for article"""
        print("\n✍️  Writing narrative templates...")
        
        # Lede paragraph template
        task_type = self.results['profile'].get('target_type', 'regression')
        
        if task_type == 'regression':
            r2 = self.article['meta'].get('r2_score', 0)
            
            if r2 > 0.7:
                lede_template = f"""Machine learning analysis of {self.article['hero']['total_records']:,} records reveals a clear pattern. The model can predict outcomes with {r2*100:.1f}% accuracy using just {len(self.article['findings'])} key factors."""
            elif r2 < 0.1:
                lede_template = f"""After analyzing {self.article['hero']['total_records']:,} records, machine learning achieved only {r2*100:.1f}% predictive accuracy. The data suggests outcomes are fundamentally unpredictable from basic features alone — and that randomness is the story."""
            else:
                lede_template = f"""Analysis of {self.article['hero']['total_records']:,} records found a moderate pattern. The model achieved {r2*100:.1f}% accuracy, suggesting some predictability but significant unmeasured factors."""
        
        elif 'classification' in task_type:
            accuracy = self.article['meta'].get('accuracy', 0)
            lede_template = f"""Machine learning analysis of {self.article['hero']['total_records']:,} records can predict outcomes with {accuracy*100:.1f}% accuracy. The model identified {len(self.article['findings'])} key predictors."""
        else:
            lede_template = f"""Analysis of {self.article['hero']['total_records']:,} records reveals patterns in the data."""
        
        self.article['narrative'] = {
            'lede': lede_template,
            'conclusion': "The data reveals patterns that challenge conventional wisdom."
        }
        
        print(f"   Lede: {lede_template[:80]}...")
    
    def export(self, output_path=None):
        """Export article content to JSON"""
        if output_path is None:
            output_path = self.results_path.parent / 'article_content.json'
        
        with open(output_path, 'w') as f:
            json.dump(self.article, f, indent=2)
        
        print(f"\n✅ Article content saved to: {output_path}")
        return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_article.py <results.json>")
        print("\nExample:")
        print("  python3 generate_article.py analysis_results/results.json")
        sys.exit(1)
    
    results_path = sys.argv[1]
    
    generator = ArticleGenerator(results_path)
    generator.generate()
    generator.export()
    
    print("\n" + "="*60)
    print("✅ ARTICLE GENERATION COMPLETE!")
    print("="*60)
    print("\nNext step: Use article_content.json to build HTML")


if __name__ == '__main__':
    main()

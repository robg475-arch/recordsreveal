#!/usr/bin/env python3
"""
Process FEC data to analyze dark money in swing House districts
Combines independent expenditures with candidate results
"""

import csv
import json
from collections import defaultdict
from datetime import datetime

# Known swing districts from 2024 (these were competitive)
SWING_DISTRICTS = {
    'CA13', 'CA22', 'CA27', 'CA40', 'CA41', 'CA45', 'CA47', 'CA49',  # California
    'CO08',  # Colorado
    'IA01', 'IA03',  # Iowa
    'ME02',  # Maine
    'MI03', 'MI07', 'MI08',  # Michigan
    'NE02',  # Nebraska
    'NJ07',  # New Jersey
    'NM02',  # New Mexico
    'NV01', 'NV03', 'NV04',  # Nevada
    'NY03', 'NY04', 'NY17', 'NY18', 'NY19', 'NY22',  # New York
    'OH01', 'OH09', 'OH13',  # Ohio
    'OR05', 'OR06',  # Oregon
    'PA07', 'PA08', 'PA10', 'PA17',  # Pennsylvania
    'VA02', 'VA07',  # Virginia
    'WA03', 'WA08',  # Washington
    'AK00',  # Alaska (at-large)
}

def load_candidates():
    """Load candidate data from weball24.txt"""
    candidates = {}
    
    with open('weball24.txt', 'r', encoding='latin-1') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) < 20:
                continue
            
            cand_id = parts[0]
            name = parts[1]
            status = parts[2]
            party = parts[4]
            state = parts[17]
            district = parts[18] if parts[18] else ''
            
            # Only House races
            if not cand_id.startswith('H'):
                continue
            
            candidates[cand_id] = {
                'id': cand_id,
                'name': name,
                'party': party,
                'state': state,
                'district': district,
                'status': status
            }
    
    print(f"✅ Loaded {len(candidates)} total House candidates")
    return candidates

def process_independent_expenditures(candidates):
    """Process independent expenditure data"""
    
    district_spending = defaultdict(lambda: {
        'total_for': 0,
        'total_against': 0,
        'dem_support': 0,
        'dem_oppose': 0,
        'rep_support': 0,
        'rep_oppose': 0,
        'transactions': [],
        'state': '',
        'district': ''
    })
    
    spender_totals = defaultdict(float)
    
    with open('independent_expenditure_2024.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        count = 0
        for row in reader:
            cand_id = row['cand_id']
            
            # Only candidates we care about
            if cand_id not in candidates:
                continue
            
            try:
                amount = float(row['exp_amo'])
            except (ValueError, TypeError):
                continue
            
            if amount == 0:
                continue
            
            support_oppose = row['sup_opp']  # S = support, O = oppose
            spender = row['spe_nam'].strip()
            purpose = row['pur']
            party = candidates[cand_id]['party']
            state = row['can_office_state']
            district = row['can_office_dis'].zfill(2) if row['can_office_dis'] else '00'
            district_code = f"{state}-{district}"
            
            # Store state/district
            district_spending[district_code]['state'] = state
            district_spending[district_code]['district'] = district
            
            # Track spending
            if support_oppose == 'S':
                district_spending[district_code]['total_for'] += amount
                if party == 'DEM':
                    district_spending[district_code]['dem_support'] += amount
                elif party in ['REP', 'REPUBLICAN PARTY']:
                    district_spending[district_code]['rep_support'] += amount
            else:  # O = oppose
                district_spending[district_code]['total_against'] += amount
                if party == 'DEM':
                    district_spending[district_code]['dem_oppose'] += amount
                elif party in ['REP', 'REPUBLICAN PARTY']:
                    district_spending[district_code]['rep_oppose'] += amount
            
            spender_totals[spender] += amount
            
            # Store transaction
            district_spending[district_code]['transactions'].append({
                'candidate': candidates[cand_id]['name'],
                'party': party,
                'spender': spender,
                'amount': amount,
                'support_oppose': 'Support' if support_oppose == 'S' else 'Oppose',
                'purpose': purpose,
                'date': row.get('exp_date', '')
            })
            
            count += 1
    
    print(f"✅ Processed {count:,} transactions across {len(district_spending)} districts")
    return district_spending, spender_totals

def create_combined_dataset(candidates, district_spending, spender_totals):
    """Create final CSV for pipeline"""
    
    rows = []
    
    # Get top spenders
    top_spenders = sorted(spender_totals.items(), key=lambda x: x[1], reverse=True)[:20]
    
    for district_code, spending in sorted(district_spending.items(), key=lambda x: x[1]['total_for'] + x[1]['total_against'], reverse=True):
        
        total = spending['total_for'] + spending['total_against']
        
        if total < 10000:  # Skip districts with minimal spending
            continue
        
        state = spending['state']
        district = spending['district']
        
        # Get candidates in this district from transactions
        candidates_in_district = {}
        for t in spending['transactions']:
            party = t['party']
            name = t['candidate']
            candidates_in_district[party] = name
        
        dem_candidate = candidates_in_district.get('DEM', 'N/A')
        rep_candidate = candidates_in_district.get('REP', candidates_in_district.get('REPUBLICAN PARTY', 'N/A'))
        
        # Get top spenders in this district
        district_transactions = spending['transactions']
        district_spenders = defaultdict(float)
        for t in district_transactions:
            district_spenders[t['spender']] += t['amount']
        
        top_district_spenders = sorted(district_spenders.items(), key=lambda x: x[1], reverse=True)[:3]
        top_spender_str = ' | '.join([f"{name}: ${amt:,.0f}" for name, amt in top_district_spenders])
        
        row = {
            'district': district_code,
            'state': state,
            'district_num': district,
            'dem_candidate': dem_candidate,
            'rep_candidate': rep_candidate,
            'total_spending': total,
            'spending_for': spending['total_for'],
            'spending_against': spending['total_against'],
            'dem_support': spending['dem_support'],
            'dem_oppose': spending['dem_oppose'],
            'rep_support': spending['rep_support'],
            'rep_oppose': spending['rep_oppose'],
            'net_dem_advantage': (spending['dem_support'] + spending['rep_oppose']) - (spending['rep_support'] + spending['dem_oppose']),
            'num_transactions': len(district_transactions),
            'top_spenders': top_spender_str
        }
        
        rows.append(row)
    
    # Write CSV
    output_file = 'dark_money_swing_districts_2024.csv'
    
    fieldnames = [
        'district', 'state', 'district_num',
        'dem_candidate', 'rep_candidate',
        'total_spending', 'spending_for', 'spending_against',
        'dem_support', 'dem_oppose', 'rep_support', 'rep_oppose',
        'net_dem_advantage', 'num_transactions', 'top_spenders'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✅ Created {output_file} with {len(rows)} swing districts")
    print(f"\n📊 Top 5 Districts by Total Spending:")
    for i, row in enumerate(rows[:5], 1):
        print(f"   {i}. {row['district']}: ${row['total_spending']:,.0f}")
    
    print(f"\n💰 Top 5 Spenders Overall:")
    for i, (spender, amount) in enumerate(top_spenders[:5], 1):
        print(f"   {i}. {spender}: ${amount:,.0f}")
    
    return output_file

def main():
    print("=" * 70)
    print("PROCESSING DARK MONEY IN SWING DISTRICTS")
    print("=" * 70)
    
    print("\n📂 Loading candidate data...")
    candidates = load_candidates()
    
    print("\n💸 Processing independent expenditures...")
    district_spending, spender_totals = process_independent_expenditures(candidates)
    
    print("\n🔨 Creating combined dataset...")
    output_file = create_combined_dataset(candidates, district_spending, spender_totals)
    
    print("\n" + "=" * 70)
    print("✅ PROCESSING COMPLETE")
    print("=" * 70)
    print(f"\n📄 Output: {output_file}")
    print(f"\n▶️  Ready for pipeline:")
    print(f"   cd ../..")
    print(f"   ./run_full_pipeline.sh data/campaign_finance/{output_file}")
    print()

if __name__ == "__main__":
    main()

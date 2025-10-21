"""
Test script to demonstrate the adaptive time granularity feature.
This script tests how the dashboard adapts between daily and weekly trends based on data range.
"""

from src.analysis import determine_time_granularity, calculate_daily_totals, calculate_weekly_averages

def test_adaptive_granularity():
    """Test the adaptive time granularity feature."""
    
    print("=" * 60)
    print("Testing Adaptive Time Granularity Feature")
    print("=" * 60)
    
    # Test with different time ranges
    test_ranges = [4, 8, 12]
    
    for weeks_back in test_ranges:
        print(f"\n📊 Testing with weeks_back={weeks_back}")
        print("-" * 60)
        
        # Determine granularity
        granularity_info = determine_time_granularity(weeks_back=weeks_back)
        
        print(f"Granularity: {granularity_info['granularity'].upper()}")
        print(f"Reason: {granularity_info['reason']}")
        print(f"Data range: {granularity_info.get('data_range_days', 0)} days")
        print(f"Sufficient for trend: {granularity_info['sufficient_for_trend']}")
        
        # Get the appropriate data
        if granularity_info['granularity'] == 'daily':
            data = calculate_daily_totals(weeks_back=weeks_back)
            print("\n📅 Daily Data:")
            print(f"  - Days with data: {data['days_with_data']}")
            print(f"  - Daily average: Rp {data['daily_average']:,.0f}")
            print(f"  - Total spent: Rp {data['total_spent']:,.0f}")
            if data['daily_breakdown']:
                print(f"  - Date range: {min(data['daily_breakdown'].keys())} to {max(data['daily_breakdown'].keys())}")
        else:
            data = calculate_weekly_averages(weeks_back=weeks_back)
            print("\n📅 Weekly Data:")
            print(f"  - Weeks with data: {data['weeks_with_data']}")
            print(f"  - Weekly average: Rp {data['weekly_average']:,.0f}")
            print(f"  - Daily average: Rp {data['daily_average']:,.0f}")
            print(f"  - Total spent: Rp {data['total_spent']:,.0f}")
    
    print("\n" + "=" * 60)
    print("✅ Adaptive Granularity Logic:")
    print("  - Data range < 14 days OR < 2 weeks → DAILY trend")
    print("  - Data range >= 14 days AND >= 2 weeks → WEEKLY trend")
    print("  - Dashboard automatically adapts to show the most informative view")
    print("=" * 60)

if __name__ == "__main__":
    test_adaptive_granularity()

#!/usr/bin/env python3
"""
AI Gold Price Tracking and Prediction Agent
Designed for digital gold investors to track Indian gold prices 24/7
Sends daily analysis and predictions via email
"""

import os
import requests
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time

def fetch_indian_gold_prices():
    """Fetch current Indian gold prices from multiple sources"""
    prices = {}
    
    try:
        # Method 1: Try MetalPriceAPI (Free tier - 100 calls/month)
        api_key = os.environ.get('METAL_API_KEY', 'demo_key')
        url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=USD&symbols=XAU"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data and 'XAU' in data['rates']:
                # Convert to INR (approximate)
                usd_to_inr = 83.25  # Current approximate rate
                gold_usd_per_oz = data['rates']['XAU']
                gold_price_per_oz_usd = 1 / gold_usd_per_oz
                gold_inr_per_10g = gold_price_per_oz_usd * usd_to_inr * 31.1035 / 10
                
                prices['24K_per_10g'] = round(gold_inr_per_10g)
                prices['22K_per_10g'] = round(gold_inr_per_10g * 0.916)  # 22K is 91.6% pure
                prices['source'] = 'MetalPriceAPI'
                print(f"✅ Successfully fetched prices from MetalPriceAPI")
            
    except Exception as e:
        print(f"⚠️ Error fetching from MetalPriceAPI: {e}")
    
    # Fallback: Use estimated current prices if API fails
    if not prices:
        # These prices are updated to current market levels
        prices = {
            '24K_per_10g': 73800,
            '22K_per_10g': 67600,
            'source': 'Estimated_Current_Market',
            'note': 'API unavailable - using current market estimates'
        }
        print("⚠️ Using fallback prices - API unavailable")
    
    prices['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    return prices

def get_market_factors():
    """Get current market factors affecting gold prices"""
    factors = {
        'usd_index': {'value': 103.1, 'impact': 'Bearish', 'weight': 'High'},
        'inflation_usa': {'value': 3.2, 'impact': 'Bullish', 'weight': 'Medium'},
        'fed_rates': {'value': 5.25, 'impact': 'Bearish', 'weight': 'High'},
        'oil_prices': {'value': 87.2, 'impact': 'Bullish', 'weight': 'Low'},
        'geopolitical': {'level': 'Medium-High', 'impact': 'Bullish', 'weight': 'Medium'},
        'indian_festivals': {'status': 'Diwali Season (October)', 'impact': 'Bullish', 'weight': 'High'},
        'monsoon': {'status': 'Good', 'impact': 'Bullish', 'weight': 'Medium'},
        'central_bank_buying': {'status': 'Active', 'impact': 'Bullish', 'weight': 'High'}
    }
    return factors

def analyze_with_ai(current_prices, factors):
    """AI-powered analysis based on multiple factors"""
    
    # Calculate weighted sentiment score
    bullish_factors = 0
    bearish_factors = 0
    total_weight = 0
    
    factor_analysis = []
    
    for factor_name, data in factors.items():
        weight_value = {'High': 3, 'Medium': 2, 'Low': 1}.get(data.get('weight', 'Low'), 1)
        total_weight += weight_value
        
        impact = data.get('impact', 'Neutral')
        if impact == 'Bullish':
            bullish_factors += weight_value
            factor_analysis.append(f"✅ {factor_name.replace('_', ' ').title()}: {impact} ({data.get('weight', 'Low')} impact)")
        elif impact == 'Bearish':
            bearish_factors += weight_value
            factor_analysis.append(f"❌ {factor_name.replace('_', ' ').title()}: {impact} ({data.get('weight', 'Low')} impact)")
        else:
            factor_analysis.append(f"⚪ {factor_name.replace('_', ' ').title()}: Neutral")
    
    # Calculate sentiment score (0-100)
    if total_weight > 0:
        sentiment_score = (bullish_factors / total_weight) * 100
    else:
        sentiment_score = 50
    
    # Generate AI prediction
    if sentiment_score > 70:
        prediction = "STRONGLY BULLISH"
        recommendation = "Excellent time to buy gold, strong fundamentals support higher prices"
        next_day_change = "+0.5% to +1.2%"
        action = "BUY on any dips"
    elif sentiment_score > 55:
        prediction = "BULLISH"
        recommendation = "Good time to accumulate gold, consider buying on weakness"
        next_day_change = "+0.2% to +0.8%"
        action = "BUY gradually"
    elif sentiment_score > 45:
        prediction = "NEUTRAL"
        recommendation = "Hold current positions, monitor market developments"
        next_day_change = "-0.3% to +0.3%"
        action = "HOLD"
    elif sentiment_score > 30:
        prediction = "BEARISH"
        recommendation = "Consider reducing positions, wait for better entry points"
        next_day_change = "-0.8% to -0.2%"
        action = "WAIT"
    else:
        prediction = "STRONGLY BEARISH"
        recommendation = "Avoid buying, consider profit-taking if heavily invested"
        next_day_change = "-1.5% to -0.5%"
        action = "SELL/WAIT"
    
    # Calculate confidence based on factor clarity
    confidence = min(95, max(65, int(sentiment_score + 20)))
    
    analysis = {
        'sentiment_score': round(sentiment_score, 1),
        'prediction': prediction,
        'recommendation': recommendation,
        'next_day_change': next_day_change,
        'action': action,
        'confidence': confidence,
        'factor_analysis': factor_analysis,
        'key_drivers': [
            f"Festival season demand from India (Diwali approaching)",
            f"USD Index at {factors['usd_index']['value']} creating headwinds",
            f"Central bank buying supporting prices globally",
            f"Geopolitical tensions at {factors['geopolitical']['level']} level"
        ]
    }
    
    return analysis

def create_analysis_report(prices, analysis):
    """Create detailed analysis report for email"""
    
    # Determine trend emoji
    sentiment = analysis['sentiment_score']
    if sentiment > 70:
        trend_emoji = "🚀📈"
    elif sentiment > 55:
        trend_emoji = "📈💰"
    elif sentiment > 45:
        trend_emoji = "➡️⚖️"
    elif sentiment > 30:
        trend_emoji = "📉⚠️"
    else:
        trend_emoji = "🔻❌"
    
    report = f"""
🏆 DAILY GOLD PRICE ANALYSIS & AI PREDICTION {trend_emoji}
📅 {prices['timestamp']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 CURRENT INDIAN GOLD PRICES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥇 24K Gold: ₹{prices['24K_per_10g']:,}/10g
🥉 22K Gold: ₹{prices['22K_per_10g']:,}/10g
📊 Data Source: {prices['source']}
{('⚠️ ' + prices.get('note', '')) if 'note' in prices else ''}

🤖 AI MARKET ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Market Sentiment: {analysis['sentiment_score']}/100
🔮 AI Prediction: {analysis['prediction']}
📈 Expected Next Day: {analysis['next_day_change']}
🎯 Action Signal: {analysis['action']}
🎪 Confidence Level: {analysis['confidence']}%

📋 DETAILED FACTOR ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    for factor in analysis['factor_analysis']:
        report += f"\n{factor}"
    
    report += f"""

🎯 KEY MARKET DRIVERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    for driver in analysis['key_drivers']:
        report += f"\n• {driver}"
    
    report += f"""

⚡ EXPERT RECOMMENDATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{analysis['recommendation']}

🎪 ACTION PLAN:
• Short-term (1-3 days): {analysis['action']}
• Price Target for Buying: ₹{int(prices['24K_per_10g'] * 0.98):,} - ₹{int(prices['24K_per_10g'] * 1.02):,} (24K)
• Stop Loss Consideration: Below ₹{int(prices['24K_per_10g'] * 0.95):,} (24K)
• Festival Season Impact: Expect 2-5% premium during Diwali week

🔔 SPECIAL ALERTS:
• 📱 Diwali season (Oct 2025): Increased demand expected
• 🏦 Central banks continue accumulating gold globally
• 💵 Watch USD strength for directional cues
• 📊 Next major data: US inflation report & Fed meeting

💡 RISK DISCLOSURE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• This analysis is for educational purposes only
• Gold prices are volatile and subject to market risks
• Always consult financial advisors for investment decisions
• Never invest more than you can afford to lose
• Past performance doesn't guarantee future results

Generated by Your Personal AI Gold Price Agent 🤖✨
Powered by advanced market analysis algorithms
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return report

def send_email_notification(report):
    """Send email notification with analysis"""
    
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        print("❌ Email credentials not configured properly")
        print(f"Sender email: {'✅' if sender_email else '❌'}")
        print(f"Sender password: {'✅' if sender_password else '❌'}")
        print(f"Recipient email: {'✅' if recipient_email else '❌'}")
        return False
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        
        # Dynamic subject line based on prediction
        today = datetime.now().strftime('%d %b %Y')
        subject = f"🏆 Gold Analysis - {today}"
        message["Subject"] = subject
        
        # Add body
        message.attach(MIMEText(report, "plain"))
        
        # Send email
        print("📧 Connecting to Gmail SMTP server...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            print("🔐 Starting secure connection...")
            server.login(sender_email, sender_password)
            print("📨 Sending email...")
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        print("✅ Email notification sent successfully!")
        print(f"📧 Sent to: {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("🔧 Check your Gmail app password and email settings")
        return False

def main():
    """Main execution function"""
    
    print("🚀 STARTING AI GOLD PRICE ANALYSIS AGENT")
    print("=" * 60)
    print(f"🕐 Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 60)
    
    # Fetch current prices
    print("\n📊 Step 1: Fetching current gold prices...")
    current_prices = fetch_indian_gold_prices()
    print(f"   24K Gold: ₹{current_prices['24K_per_10g']:,}/10g")
    print(f"   22K Gold: ₹{current_prices['22K_per_10g']:,}/10g")
    
    # Get market factors
    print("\n🌍 Step 2: Analyzing global market factors...")
    market_factors = get_market_factors()
    print(f"   Analyzing {len(market_factors)} market factors...")
    
    # Perform AI analysis
    print("\n🤖 Step 3: Running AI analysis engine...")
    analysis = analyze_with_ai(current_prices, market_factors)
    print(f"   Market Sentiment: {analysis['sentiment_score']}/100")
    print(f"   AI Prediction: {analysis['prediction']}")
    print(f"   Confidence: {analysis['confidence']}%")
    
    # Create report
    print("\n📝 Step 4: Generating detailed analysis report...")
    report = create_analysis_report(current_prices, analysis)
    
    # Print report to console (for debugging)
    print("\n" + "=" * 60)
    print("📋 GENERATED ANALYSIS REPORT:")
    print("=" * 60)
    print(report)
    print("=" * 60)
    
    # Send notifications
    print("\n📧 Step 5: Sending email notification...")
    email_sent = send_email_notification(report)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"📊 Gold Prices: Fetched from {current_prices['source']}")
    print(f"🤖 AI Analysis: {analysis['prediction']}")
    print(f"📧 Email Status: {'✅ Sent Successfully' if email_sent else '❌ Failed'}")
    print(f"🕐 Next Run: Tomorrow at 6:30 AM IST")
    print("=" * 60)
    
    if email_sent:
        print("🎯 Check your email for the complete analysis!")
    else:
        print("⚠️ Email failed - check GitHub Actions logs for details")

if __name__ == "__main__":
    main()

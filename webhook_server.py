"""
Webhook server for receiving leads from ad platforms and landing pages
Run this as a Flask server to receive webhook calls
"""

from flask import Flask, request, jsonify
from marketing_agent import MarketingAgent
import logging

app = Flask(__name__)
agent = MarketingAgent()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'marketing-agent-webhook'})


@app.route('/api/leads', methods=['POST'])
def receive_lead():
    """
    Receive lead from landing page or ad platform
    Expected JSON:
    {
        "name": "דני כהן",
        "phone": "050-1234567",
        "email": "danny@example.com",
        "source": "google|facebook|instagram|organic",
        "campaign": "campaign_name",
        "location": "הרצליה",
        "budget": "800000",
        "project_type": "new_build|renovation|commercial"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'phone', 'email', 'source', 'campaign']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400
        
        # Add lead to system
        lead = agent.add_lead(
            name=data['name'],
            phone=data['phone'],
            email=data['email'],
            source=data['source'],
            campaign=data['campaign'],
            location=data.get('location'),
            budget=data.get('budget'),
            project_type=data.get('project_type')
        )
        
        logger.info(f"Lead received and processed: {lead.id}")
        
        return jsonify({
            'success': True,
            'lead_id': lead.id,
            'quality_score': lead.quality_score,
            'status': lead.status
        }), 201
        
    except Exception as e:
        logger.error(f"Error processing lead: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/leads/<lead_id>/status', methods=['PUT'])
def update_lead_status(lead_id):
    """Update lead status"""
    try:
        data = request.get_json()
        status = data.get('status')
        notes = data.get('notes')
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        agent.update_lead_status(lead_id, status, notes)
        
        return jsonify({'success': True, 'lead_id': lead_id, 'status': status}), 200
        
    except Exception as e:
        logger.error(f"Error updating lead status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get leads with optional filters"""
    try:
        status = request.args.get('status')
        min_score = request.args.get('min_score', type=int)
        
        if status:
            leads = agent.get_leads_by_status(status)
        elif min_score:
            leads = agent.get_high_quality_leads(min_score)
        else:
            leads = agent.leads
        
        # Convert to dict for JSON serialization
        leads_data = [{
            'id': lead.id,
            'name': lead.name,
            'phone': lead.phone,
            'email': lead.email,
            'source': lead.source,
            'campaign': lead.campaign,
            'status': lead.status,
            'quality_score': lead.quality_score,
            'timestamp': lead.timestamp
        } for lead in leads]
        
        return jsonify({
            'success': True,
            'count': len(leads_data),
            'leads': leads_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting leads: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/campaigns/metrics', methods=['POST'])
def add_campaign_metrics():
    """Add campaign performance metrics"""
    try:
        data = request.get_json()
        
        required_fields = ['campaign_id', 'campaign_name', 'platform', 
                          'impressions', 'clicks', 'conversions', 'cost']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400
        
        metrics = agent.add_campaign_metrics(
            campaign_id=data['campaign_id'],
            campaign_name=data['campaign_name'],
            platform=data['platform'],
            impressions=data['impressions'],
            clicks=data['clicks'],
            conversions=data['conversions'],
            cost=data['cost']
        )
        
        return jsonify({
            'success': True,
            'metrics': {
                'cpl': metrics.cpl,
                'ctr': metrics.ctr,
                'conversion_rate': metrics.conversion_rate
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding campaign metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/report', methods=['GET'])
def get_report():
    """Get performance report"""
    try:
        days = request.args.get('days', default=30, type=int)
        report = agent.get_performance_report(days=days)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/optimize', methods=['GET'])
def get_optimization_recommendations():
    """Get campaign optimization recommendations"""
    try:
        recommendations = agent.optimize_campaigns()
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Marketing Agent Webhook Server...")
    print("Endpoints:")
    print("  POST /api/leads - Receive new lead")
    print("  GET  /api/leads - Get leads")
    print("  PUT  /api/leads/<id>/status - Update lead status")
    print("  POST /api/campaigns/metrics - Add campaign metrics")
    print("  GET  /api/report - Get performance report")
    print("  GET  /api/optimize - Get optimization recommendations")
    print()
    
    # Run on port 5000 by default
    app.run(host='0.0.0.0', port=5000, debug=True)

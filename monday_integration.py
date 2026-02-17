"""
Monday.com Integration Module
Placeholder for future Monday.com API integration
"""

import requests
import json
from typing import List, Dict
from marketing_agent import Lead


class MondayIntegration:
    """Monday.com API integration"""
    
    def __init__(self, api_key: str = None, board_id: str = None):
        """
        Initialize Monday.com integration
        
        Args:
            api_key: Monday.com API key
            board_id: Monday.com board ID for leads
        """
        self.api_key = api_key
        self.board_id = board_id
        self.api_url = "https://api.monday.com/v2"
        
    def is_configured(self) -> bool:
        """Check if Monday.com is configured"""
        return bool(self.api_key and self.board_id)
    
    def sync_lead(self, lead: Lead) -> Dict:
        """
        Sync a single lead to Monday.com
        
        Args:
            lead: Lead object to sync
            
        Returns:
            Dict with sync result
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Monday.com not configured. Add API key and board ID to config.json'
            }
        
        # Monday.com GraphQL mutation
        mutation = """
        mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
            create_item (board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
                id
            }
        }
        """
        
        # Map lead data to Monday.com columns
        column_values = {
            "text": lead.name,  # Name column
            "phone": {"phone": lead.phone, "countryShortName": "IL"},  # Phone column
            "email": {"email": lead.email, "text": lead.email},  # Email column
            "status": {"label": lead.status},  # Status column
            "text6": lead.source,  # Source column
            "text7": lead.campaign or "",  # Campaign column
            "numbers": lead.quality_score or 0,  # Quality score column
            "text8": lead.location or "",  # Location column
            "text9": lead.budget or "",  # Budget column
            "text10": lead.project_type or "",  # Project type column
            "text11": lead.notes or "",  # Notes column
        }
        
        variables = {
            "boardId": self.board_id,
            "itemName": f"{lead.name} - {lead.id}",
            "columnValues": json.dumps(column_values)
        }
        
        try:
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                json={"query": mutation, "variables": variables},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    return {'success': False, 'error': str(data['errors'])}
                return {'success': True, 'item_id': data.get('data', {}).get('create_item', {}).get('id')}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_leads(self, leads: List[Lead]) -> Dict:
        """
        Sync multiple leads to Monday.com
        
        Args:
            leads: List of Lead objects
            
        Returns:
            Dict with sync results
        """
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for lead in leads:
            result = self.sync_lead(lead)
            if result.get('success'):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'lead_id': lead.id,
                    'error': result.get('error')
                })
        
        return results
    
    def update_lead_status(self, monday_item_id: str, status: str) -> Dict:
        """
        Update lead status in Monday.com
        
        Args:
            monday_item_id: Monday.com item ID
            status: New status
            
        Returns:
            Dict with update result
        """
        if not self.is_configured():
            return {'success': False, 'error': 'Monday.com not configured'}
        
        mutation = """
        mutation ($itemId: ID!, $columnValues: JSON!) {
            change_column_value (item_id: $itemId, column_values: $columnValues) {
                id
            }
        }
        """
        
        variables = {
            "itemId": monday_item_id,
            "columnValues": json.dumps({"status": {"label": status}})
        }
        
        try:
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                json={"query": mutation, "variables": variables},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    return {'success': False, 'error': str(data['errors'])}
                return {'success': True}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Instructions for setup:
"""
To integrate Monday.com:

1. Get Monday.com API Key:
   - Go to https://monday.com
   - Click on your profile → Admin → API
   - Generate a new API token

2. Create a Board for Leads:
   - Create a new board called "Marketing Leads"
   - Add columns:
     * Name (text)
     * Phone (phone)
     * Email (email)
     * Status (status)
     * Source (text)
     * Campaign (text)
     * Quality Score (numbers)
     * Location (text)
     * Budget (text)
     * Project Type (text)
     * Notes (text)
   - Copy the Board ID from the URL

3. Add to config.json:
   {
     "monday": {
       "api_key": "your_api_key_here",
       "board_id": "your_board_id_here"
     }
   }

4. Use in app.py:
   from monday_integration import MondayIntegration
   
   monday = MondayIntegration(
       api_key=config['monday']['api_key'],
       board_id=config['monday']['board_id']
   )
   
   result = monday.sync_lead(lead)
"""

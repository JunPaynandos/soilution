import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from detector.models import CropRecommendation, Workspace

class Command(BaseCommand):
    help = 'Populates the database with 200 dummy crop recommendation records for the last month.'

    def handle(self, *args, **kwargs):
        # Target the specific workspace the user is viewing (ID: 135)
        try:
            workspace = Workspace.objects.get(id=135)
        except Workspace.DoesNotExist:
            # Fallback to first if 135 doesn't exist (though we know it does from logs)
            workspace = Workspace.objects.first()
            
        if not workspace:
            self.stdout.write(self.style.ERROR('No workspace found. Please create a workspace first.'))
            return

        # Clear existing records to ensure only the correct crops are shown
        self.stdout.write(f'Clearing old records for workspace "{workspace.name}"...')
        CropRecommendation.objects.filter(workspace=workspace).delete()

        crops = [
            'apple', 'banana', 'blackgram', 'chickpea', 'coconut', 'coffee', 'cotton', 'grapes', 
            'jute', 'kidneybeans', 'lentil', 'maize', 'mango', 'mothbeans', 'mungbean', 'muskmelon', 
            'orange', 'papaya', 'pigeonpeas', 'pomegranate', 'rice', 'watermelon', 'wheat'
        ]
        
        # Generate 200 records
        records_to_create = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        self.stdout.write('Generating 200 dummy records...')

        for _ in range(200):
            # Random timestamp within the last 30 days
            random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
            timestamp = start_date + timedelta(seconds=random_seconds)

            # Random soil data
            nitrogen = random.uniform(0, 100)
            phosphorus = random.uniform(0, 100)
            potassium = random.uniform(0, 100)
            temperature = random.uniform(20, 35)
            moisture = random.uniform(30, 90)
            ph = random.uniform(5.5, 8.0)
            conductivity = random.uniform(0, 5)
            
            # Random recommendation
            recommended_crop = random.choice(crops)
            confidence = random.uniform(70, 99)
            
            # Dummy all_recommendations
            all_recs = [
                {'name': recommended_crop, 'confidence': round(confidence, 2)},
                {'name': random.choice([c for c in crops if c != recommended_crop]), 'confidence': round(random.uniform(40, 60), 2)},
                {'name': random.choice([c for c in crops if c != recommended_crop]), 'confidence': round(random.uniform(10, 30), 2)},
            ]

            # Create object (we will update timestamp later because of auto_now_add)
            record = CropRecommendation(
                workspace=workspace,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                temperature=temperature,
                moisture=moisture,
                ph=ph,
                conductivity=conductivity,
                recommended_crop=recommended_crop,
                confidence=confidence,
                all_recommendations=all_recs
            )
            record.save()
            
            # Manually update timestamp
            record.timestamp = timestamp
            record.save(update_fields=['timestamp'])

        self.stdout.write(self.style.SUCCESS(f'Successfully created 200 crop recommendation records for workspace "{workspace.name}".'))

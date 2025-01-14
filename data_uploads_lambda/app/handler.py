import json
import csv
import base64
import io
from sqlalchemy import create_engine, text
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        logger.info("Starting CSV upload process")
        
        # Get CSV content from event
        csv_content = base64.b64decode(event['csv_content']).decode('utf-8')
        database_url = os.environ['DATABASE_URL']
        logger.info("CSV content decoded")
        
        # Parse CSV
        csv_file = io.StringIO(csv_content)
        csv_reader = csv.DictReader(csv_file)
        records = list(csv_reader)
        logger.info(f"Parsed {len(records)} records from CSV")
        
        # Create engine
        logger.info("Creating database engine")
        engine = create_engine(database_url, connect_args={'connect_timeout': 10}, pool_recycle=3600, pool_pre_ping=True, pool_timeout=10)
        
        # Create table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS loads (
            reference_number VARCHAR PRIMARY KEY,
            origin VARCHAR NOT NULL,
            destination VARCHAR NOT NULL,
            equipment_type VARCHAR NOT NULL,
            rate FLOAT NOT NULL,
            commodity VARCHAR NOT NULL
        )
        """
        
        insert_sql = """
        INSERT INTO loads (reference_number, origin, destination, equipment_type, rate, commodity)
        VALUES (:reference_number, :origin, :destination, :equipment_type, :rate, :commodity)
        ON CONFLICT (reference_number) DO UPDATE SET
            origin = EXCLUDED.origin,
            destination = EXCLUDED.destination,
            equipment_type = EXCLUDED.equipment_type,
            rate = EXCLUDED.rate,
            commodity = EXCLUDED.commodity
        """
        
        logger.info("Executing database operations")
        with engine.connect() as conn:

            conn = conn.execution_options(timeout=10)

            # Create table
            conn.execute(text(create_table_sql))
            logger.info("Table created/verified")
            
            # Insert records
            conn.execute(text(insert_sql), records)
            conn.commit()
            logger.info("Records inserted successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully uploaded {len(records)} records',
                'record_count': len(records)
            })
        }
    except Exception as e:
        logger.error(f"Error during upload: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
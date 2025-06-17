#!/usr/bin/env python3
"""
Manual sync Text2SQL resources
"""
import asyncio
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.services.resource_discovery.resource_discovery_service import ResourceDiscoveryService
from src.config.database import DATABASE_URL

async def manual_sync_text2sql():
    """Manually sync Text2SQL resources"""
    try:
        print("=== Manual Text2SQL Resource Sync ===")
        
        # Create database session
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        try:
            # 1. Discover Text2SQL resources
            service = ResourceDiscoveryService()
            text2sql_resources = await service._discover_text2sql_resources_with_tools()
            
            print(f"Discovered {len(text2sql_resources)} Text2SQL resources")
            
            # 2. Check existing resources
            existing_query = text("""
                SELECT resource_id, resource_name 
                FROM resource_discovery.resource_registry 
                WHERE resource_type = 'TEXT2SQL'
                ORDER BY resource_id
            """)
            
            existing_result = session.execute(existing_query)
            existing_resources = existing_result.fetchall()
            
            print(f"\nExisting Text2SQL resources: {len(existing_resources)}")
            for res in existing_resources:
                print(f"  - {res.resource_id}: {res.resource_name}")
            
            # 3. Insert missing resources
            print(f"\nInserting missing resources...")
            
            for resource in text2sql_resources:
                resource_id = resource['resource_id']
                
                # Check if resource already exists
                check_query = text("""
                    SELECT COUNT(*) as count 
                    FROM resource_discovery.resource_registry 
                    WHERE resource_id = :resource_id
                """)
                
                check_result = session.execute(check_query, {"resource_id": resource_id})
                exists = check_result.fetchone().count > 0
                
                if not exists:
                    print(f"  Inserting: {resource_id}")
                    
                    # Insert new resource
                    insert_query = text("""
                        INSERT INTO resource_discovery.resource_registry (
                            resource_id, resource_name, resource_type, description,
                            capabilities, tags, metadata, source_table, source_id,
                            is_active, status, created_at, updated_at
                        ) VALUES (
                            :resource_id, :resource_name, :resource_type, :description,
                            :capabilities, :tags, :metadata, :source_table, :source_id,
                            :is_active, :status, NOW(), NOW()
                        )
                    """)
                    
                    session.execute(insert_query, {
                        "resource_id": resource['resource_id'],
                        "resource_name": resource['resource_name'],
                        "resource_type": resource['resource_type'].value if hasattr(resource['resource_type'], 'value') else resource['resource_type'],
                        "description": resource['description'],
                        "capabilities": json.dumps(resource['capabilities']),  # Convert to JSON string
                        "tags": json.dumps(resource['tags']),  # Convert to JSON string
                        "metadata": json.dumps(resource['metadata']),  # Convert to JSON string
                        "source_table": resource['source_table'],
                        "source_id": resource['source_id'],
                        "is_active": resource['is_active'],
                        "status": resource['status'].value if hasattr(resource['status'], 'value') else resource['status']
                    })
                    
                    print(f"    ✅ Inserted {resource_id}")
                else:
                    print(f"  Skipping: {resource_id} (already exists)")
            
            # 4. Commit changes
            session.commit()
            print(f"\n✅ Manual sync completed successfully!")
            
            # 5. Verify results
            final_query = text("""
                SELECT COUNT(*) as count 
                FROM resource_discovery.resource_registry 
                WHERE resource_type = 'TEXT2SQL'
            """)
            
            final_result = session.execute(final_query)
            final_count = final_result.fetchone().count
            
            print(f"Final Text2SQL resource count: {final_count}")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error during sync: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(manual_sync_text2sql())

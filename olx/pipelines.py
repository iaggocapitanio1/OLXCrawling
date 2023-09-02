from itemadapter import ItemAdapter
import pymongo
import csv


class OlxPipeline:

    def __init__(self):
        from olx import settings

        # Try to connect to MongoDB
        try:
            self.conn = pymongo.MongoClient(host=settings.DATABASE['host'], port=int(settings.DATABASE['port']),
                                            username=settings.DATABASE['user'],
                                            password=settings.DATABASE['password'], )
            db = self.conn[settings.DATABASE['db']]
            self.collection = db[settings.DATABASE['collection']]
            self.db_connected = True
        except Exception as e:
            print(f"Failed to connect to MongoDB due to: {e}. Data will be saved to a CSV file.")
            self.db_connected = False
            self.csvfile = open("output.csv", "w", newline='', encoding="utf-8")
            self.csvwriter = csv.DictWriter(self.csvfile,
                                            fieldnames=["id", "price"])  # Assuming item has "id" and "price" fields
            self.csvwriter.writeheader()

    def process_item(self, item, spider):
        if self.db_connected:
            try:
                self.collection.insert_one(ItemAdapter(item).asdict())
            except Exception as e:
                spider.logger.error(f"Error inserting item into MongoDB: {e}")
        else:
            # If DB connection failed, write to CSV
            self.csvwriter.writerow(ItemAdapter(item).asdict())
        return item

    def close_spider(self, spider):
        if not self.db_connected:
            # Close the CSV file if DB connection failed
            self.csvfile.close()
        else:
            self.conn.close()

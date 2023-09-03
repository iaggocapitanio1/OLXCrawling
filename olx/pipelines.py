from itemadapter import ItemAdapter
import pymongo

class OlxPipeline:

    def __init__(self):
        from olx import settings

        # Connect to MongoDB
        self.conn = pymongo.MongoClient(
            host=settings.DATABASE['host'],
            port=int(settings.DATABASE['port']),
            username=settings.DATABASE['user'],
            password=settings.DATABASE['password']
        )
        db = self.conn[settings.DATABASE['db']]
        self.collection = db[settings.DATABASE['collection']]

    def process_item(self, item, spider):
        try:
            self.collection.insert_one(ItemAdapter(item).asdict())
        except Exception as e:
            spider.logger.error(f"Error inserting item into MongoDB: {e}")
        return item

    def close_spider(self, spider):
        self.conn.close()

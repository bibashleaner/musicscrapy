# import pymongo
# from itemadapter import ItemAdapter

# class MusicPipeline:
#     def process_item(self, item, spider):
#         return item

import pymongo
from itemadapter import ItemAdapter

class MongoDBPipeline:
    name = "songs"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "musicmongo")
        )

    def open_spider(self, spider):
        db_name = str(self.mongo_db)
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # Create unique index on URL
        self.db[self.name].create_index("url", unique=True)
       
        def close_spider(self, spider):
            self.client.close()

        def process_item(self, item, spider):
            try:
                # Upsert based on URL
                self.db[self.name].update_one(
                    {"url": item["url"]},
                    {"$setOnInsert": ItemAdapter(item).asdict()},
                    upsert=True
                )
            except Exception as e:
                spider.logger.error(f"Database error: {e}")
            return item

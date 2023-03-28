import uuid, datetime
from lib.db import db, POST_INDEX, COMMENT_INDEX, LIKE_INDEX, es
from lib.user import user
import tekore as tk 
from elasticsearch_dsl import Search
#create, destroy, comment/like posts


class Post:
    '''
    All Post functions
    
    '''
    def __init__(self, token) -> None:
        self.token  = token
        self.datetime = str(datetime.datetime.now(datetime.timezone.utc))
        return
     
    def create_post(self, song, blurb) -> bool:
        '''
        '''
        post ={
            "id" : str(uuid.uuid4()),
            "date_time" : self.datetime,
            "friend_id" : user(self.token).get_friend_id(),
            "sond_id" : song,
            "text_blurb" : blurb
            } 
        return db.commit_document(POST_INDEX, post)  
        
    def delete_post(self, post_id) -> bool:
        '''
        '''
        if db.get_owner(POST_INDEX, post_id) == user(self.token).get_friend_id():
            return db.delete_document(type=POST_INDEX, id=post_id)
        return False
    
    def add_comment(self, post_id, blurb)->bool:
        '''
        '''
        try:
            comment = {
                "id" : str(uuid.uuid4()),
                "date_time" : self.datetime,
                "post_id" : post_id,
                "friend_id" : user(self.token).get_friend_id(),
                "text_blurb" : blurb
                }
            return db.commit_document(POST_INDEX, comment)  
        except:
            return False
        
    def delete_comment(self,cid)-> bool:
        '''
        '''
        if db.get_owner(COMMENT_INDEX, cid) == user(self.token).get_friend_id():
            return db.delete_document(type=COMMENT_INDEX, id=cid)
        return False
        
    def like_unlike_post(self, post_id) -> bool:
        '''
        '''
        friend_id = user(self.token).get_friend_id()
        s = Search(using=es, index=LIKE_INDEX) \
            .query("match", friend_id = friend_id) \
            .query("match", post_id= post_id)
        response = s.execute() 
        if response.hits.total["value"] > 0:
            like = {
                "friend_id": friend_id,
                "post_id" : post_id,
                "date_time": self.datetime
            }
            if db.commit_document(LIKE_INDEX, doc=like):
                return True 
            
        else:
            db.delete_document(LIKE_INDEX, user=friend_id, id=post_id)
            return False

    def get_post_likes(self, post_id) -> int:
        '''
        '''
        friend_id = user(self.token).get_friend_id()
        s = Search(using=es, index=LIKE_INDEX) \
            .query("match", post_id= post_id)
        response = s.execute() 
        return response.hits.total["value"]
    
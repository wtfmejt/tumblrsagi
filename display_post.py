#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     26/05/2015
# Copyright:   (c) User 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#External
import sqlalchemy# Database  library
# Project-local
from utils import * # General utility functions
import sql_functions# Database interaction
import config # Settings and configuration
from tables import *# Table definitions



def display_post(session,source_id,output_path="debug\\post.txt"):
    """Display a single post"""
    page = "Tumblr post number:"+repr(source_id)+"\r\n"
    # Get post row
    post_query = sqlalchemy.select([twkr_posts]).\
        where(twkr_posts.source_id == source_id)
    post_rows = session.execute(post_query)
    post_row = post_rows.fetchone()
    logging.debug("post_row:"+repr(post_row))
    page += "post_row:"+repr(post_row)+"\r\n"

    # Get post subrows
    logging.debug("Post type is: "+sql_functions.reverse_map_post_type(post_row.post_type))

    # 1: u'text',
    if post_row.post_type == 1:
        text_query = sqlalchemy.select([twkr_posts_text]).\
            where(twkr_posts_text.post_id == source_id)
        text_rows = session.execute(text_query)
        text_row = text_rows.fetchone()
        logging.debug("text_row:"+repr(text_row))
        page += "text_row:"+repr(text_row)+"\r\n"

    # 2: u'photo',
    # 3: u'quote',
    # 4: u'link',
    # 5: u'chat',
    # 6: u'audio',
    # 7: u'video',
    # 8: u'answer'

    # Get blog row
    blog_query = sqlalchemy.select([twkr_blogs]).\
        where(twkr_blogs.blog_id == post_row.blog_id)
    blog_rows = session.execute(blog_query)
    blog_row = blog_rows.fetchone()
    logging.debug("blog_row:"+repr(blog_row))
    page += "blog_row:"+repr(blog_row)+"\r\n"

    page += "\r\nMedia associated with this post:\r\n"

    # Get media hashes
    hash_query = sqlalchemy.select([media_associations]).\
        where(media_associations.post_id == post_row.post_id)
    hash_rows = session.execute(hash_query)
    for hash_row in hash_rows:
        # Add hash info to page
        page +="hash_row:"+repr(hash_row)+"\r\n"

        # Load media info for the hash
        media_query = sqlalchemy.select([Media]).\
            where(Media.sha512base64_hash == hash_row.sha512base64_hash)
        media_rows = session.execute(media_query)
        for media_row in media_rows:
            page += "media_row:"+repr(media_row)+"\r\n"

        page += "\r\n"

    # Show the raw_post data for comparison
    raw_post_query = sqlalchemy.select([RawPosts]).\
        where(RawPosts.all_posts_id == source_id)
    raw_post_rows = session.execute(raw_post_query)
    raw_post_row = raw_post_rows.fetchone()
    page +="raw_post_row:"+repr(raw_post_row)+"\r\n"

    # Save page to disk
    save_file(
        file_path=output_path,
        data=page,
        force_save=True,
        allow_fail=False
        )
    return


def list_domain_posts(session,blog_domain,output_path="debug\\list_posts.txt"):
    """List all posts for a given domain"""
    page = "Posts for blog:"+repr(blog_domain)+"\r\n"

    # Get blog id
    blog_query = sqlalchemy.select([twkr_blogs]).\
        where(twkr_blogs.blog_url == blog_domain)
    blog_rows = session.execute(blog_query)
    blog_row = blog_rows.fetchone()
    page +="blog_row:"+repr(blog_row)+"\r\n"

    # Find all posts for this blog
    post_query = sqlalchemy.select([twkr_posts]).\
        where(twkr_posts.blog_id == blog_row.blog_id)
    post_rows = session.execute(post_query)
    for post_row in post_rows:
        # Add hash info to page
        page +="post_row:"+repr(post_row)+"\r\n"

    # Save page to disk
    save_file(
        file_path=output_path,
        data=page,
        force_save=True,
        allow_fail=False
        )
    return


def list_blogs(session,output_path="debug\\blog_list.txt"):
    """Generate a list of blogs in the DB"""
    page = "Blogs:"+"\r\n"

    # Find blogs
    blog_query = sqlalchemy.select([twkr_blogs])
    blog_rows = session.execute(blog_query)
    for blog_row in blog_rows:
        # Add hash info to page
        page +="blog_row:"+repr(blog_row)+"\r\n"

    # Save page to disk
    save_file(
        file_path=output_path,
        data=page,
        force_save=True,
        allow_fail=False
        )
    return


def main():
    try:
        setup_logging(
        log_file_path=os.path.join("debug","display_post-log.txt"),
        concise_log_file_path=os.path.join("debug","short-display_post-log.txt")
        )
        # Program
        session = sql_functions.connect_to_db()

        display_post(
            session,
            source_id = 118863575131,
            output_path="debug\\post.txt"
            )

        list_domain_posts(
            session,
            blog_domain = "askbuttonsmom.tumblr.com",
            output_path="debug\\list_posts.txt"
            )

        list_blogs(
        session,
        output_path="debug\\blog_list.txt"
        )
        # /Program
        logging.info("Finished, exiting.")
        return

    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return

if __name__ == '__main__':
    main()
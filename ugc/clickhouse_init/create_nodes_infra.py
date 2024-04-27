import logging

from clickhouse_driver import Client

from config import settings


def create_tables_for_first_node():
    logging.info('Prepare to create databases on first node')
    client = Client(host='clickhouse-node1',
                    user=settings.clickhouse_username,
                    password=settings.clickhouse_password)
    logging.info('Client created')

    client.execute('CREATE DATABASE IF NOT EXISTS shard_db;')
    client.execute('CREATE DATABASE IF NOT EXISTS replica_db;')

    # create player_progress table
    client.execute(
        "CREATE TABLE IF NOT EXISTS shard_db.player_progress "
        "(user_id UUID, movie_id UUID, event_dt DateTime, view_progress Int64, movie_duration Int64) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/player_progress', 'replica_1') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.player_progress "
        "(user_id UUID, movie_id UUID, event_dt DateTime, view_progress Int64, movie_duration Int64) "
        "ENGINE = Distributed('ugc_cluster', '', player_progress, rand());")

    # create player_settings_events table
    client.execute(
        "CREATE TABLE IF NOT EXISTS shard_db.player_settings_events "
        "(user_id UUID, movie_id UUID, event_dt DateTime, event_type String) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/player_settings_events', 'replica_1') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.player_settings_events "
        "(user_id UUID, movie_id UUID, event_dt DateTime, event_type String) "
        "ENGINE = Distributed('ugc_cluster', '', player_settings_events, rand());")

    # # create player_settings_events click_events
    client.execute(
        "CREATE TABLE IF NOT EXISTS shard_db.click_events "
        "(user_id UUID, event_dt DateTime, current_url String NULL, destination_url String NULL) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/click_events', 'replica_1') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.click_events "
        "(user_id UUID, event_dt DateTime, current_url String NULL, destination_url String NULL) "
        "ENGINE = Distributed('ugc_cluster', '', click_events, rand());")

    # # create bookmarks
    client.execute(
        "CREATE TABLE IF NOT EXISTS shard_db.bookmarks "
        "(user_id UUID, movie_id UUID, is_delete Bool, event_dt DateTime) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/bookmarks', 'replica_1') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.bookmarks "
        "(user_id UUID, movie_id UUID, is_delete Bool, event_dt DateTime) "
        "ENGINE = Distributed('ugc_cluster', '', bookmarks, rand());")

    # create review
    client.execute(
        "CREATE TABLE IF NOT EXISTS shard_db.reviews "
        "(id UUID, user_id UUID, movie_id UUID, score Int8, text LONGTEXT, is_delete Bool, event_dt DateTime) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/reviews', 'replica_1') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.reviews "
        "(id UUID, user_id UUID, movie_id UUID, score Int8, text LONGTEXT, is_delete Bool, event_dt DateTime) "
        "ENGINE = Distributed('ugc_cluster', '', reviews, rand());")

    # create review_rating
    client.execute(
        "CREATE TABLE IF NOT EXISTS shard_db.review_ratings "
        "(user_id UUID, review_id UUID, score Int8, is_delete Bool, event_dt DateTime) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/review_ratings', 'replica_1') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.review_ratings "
        "(user_id UUID, review_id UUID, score Int8, is_delete Bool, event_dt DateTime) "
        "ENGINE = Distributed('ugc_cluster', '', review_ratings, rand());")

    shard_db_tables = client.execute('SHOW TABLES FROM shard_db')
    if shard_db_tables != [('click_events',), ('player_progress',), ('player_settings_events',)]:
        logging.error("Required tables don't exist on first node (shard_db)!")
        raise Exception

    replica_db_tables = client.execute('SHOW TABLES FROM replica_db')
    if replica_db_tables != [('click_events',), ('player_progress',), ('player_settings_events',)]:
        logging.error("Required tables don't exist on first node (replica_db)!")
        raise Exception

    logging.info("Tables successfully created on first node!")


def create_tables_for_second_node():
    logging.info('Prepare to create databases on second node')
    client = Client(host='clickhouse-node2',
                    user=settings.clickhouse_username,
                    password=settings.clickhouse_password)
    logging.info('Client created')

    client.execute('CREATE DATABASE IF NOT EXISTS replica_db;')

    # create player_progress table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.player_progress "
        "(user_id UUID, movie_id UUID, event_dt DateTime, view_progress Int64, movie_duration Int64) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/player_progress', 'replica_2') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create player_settings_events table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.player_settings_events "
        "(user_id UUID, movie_id UUID, event_dt DateTime, event_type String) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/player_settings_events', 'replica_2') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create click_events table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.click_events "
        "(user_id UUID, event_dt DateTime, current_url String NULL, destination_url String NULL) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/click_events', 'replica_2') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create bookmarks table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.bookmarks "
        "(user_id UUID, movie_id UUID, is_delete Bool, event_dt DateTime) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/bookmarks', 'replica_2') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create review table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.reviews "
        "(id UUID, user_id UUID, movie_id UUID, score Int8, text LONGTEXT, is_delete Bool, event_dt DateTime) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/reviews', 'replica_2') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create review_rating table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.review_ratings "
        "(user_id UUID, review_id UUID, score Int8, is_delete Bool, event_dt DateTime) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/review_ratings', 'replica_2') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    tables = client.execute('SHOW TABLES FROM replica_db')
    if tables != [('click_events',), ('player_progress',), ('player_settings_events',)]:
        logging.error("Required tables don't exist on second node (replica_db)!")
        raise Exception

    logging.info("Tables successfully created on second node!")


def create_tables_for_third_node():
    logging.info('Prepare to create databases on third node')
    client = Client(host='clickhouse-node3',
                    user=settings.clickhouse_username,
                    password=settings.clickhouse_password)
    logging.info('Client created')

    client.execute('CREATE DATABASE IF NOT EXISTS replica_db;')

    # create player_progress table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.player_progress "
        "(user_id UUID, movie_id UUID, event_dt DateTime, view_progress Int64, movie_duration Int64) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/player_progress', 'replica_3') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create player_settings_events table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.player_settings_events "
        "(user_id UUID, movie_id UUID, event_dt DateTime, event_type String) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/player_settings_events', 'replica_3') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create click_events table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.click_events "
        "(user_id UUID, event_dt DateTime, current_url String NULL, destination_url String NULL) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/click_events', 'replica_3') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create bookmarks table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.bookmarks "
        "(user_id UUID, movie_id UUID, is_delete Bool, event_dt DateTime) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/bookmarks', 'replica_3') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create review table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.reviews "
        "(id UUID, user_id UUID, movie_id UUID, score Int8, text LONGTEXT, is_delete Bool, event_dt DateTime) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/reviews', 'replica_3') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    # create review_rating table
    client.execute(
        "CREATE TABLE IF NOT EXISTS replica_db.review_ratings "
        "(user_id UUID, review_id UUID, score Int8, is_delete Bool, event_dt DateTime) "
        "Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/review_ratings', 'replica_3') "
        "PARTITION BY toYYYYMMDD(event_dt) ORDER BY event_dt;")

    tables = client.execute('SHOW TABLES FROM replica_db')
    if tables != [('click_events',), ('player_progress',), ('player_settings_events',)]:
        logging.error("Required tables don't exist on third node (replica_db)!")
        raise Exception

    logging.info("Tables successfully created on third node!")


def main():
    try:
        create_tables_for_first_node()
        create_tables_for_second_node()
        create_tables_for_third_node()
    except Exception as e:
        logging.error(f'{e.__class__.__name__}: \n {str(e)}')


if __name__ == '__main__':
    main()

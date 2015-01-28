from contextlib import contextmanager
from datetime import date
import re

import MySQLdb


def main():
    with get_con() as (db, cursor):
        cursor.execute('DELETE FROM advocate.magazine_content_contributors')
        cursor.execute('DELETE FROM advocate.magazine_contributor')
        cursor.execute('DELETE FROM advocate.magazine_content_tags')
        cursor.execute('DELETE FROM advocate.magazine_tag')
        cursor.execute('DELETE FROM advocate.magazine_article')
        cursor.execute('DELETE FROM advocate.magazine_image')
        cursor.execute('DELETE FROM advocate.magazine_content')
        cursor.execute('DELETE FROM advocate.magazine_section')
        cursor.execute('DELETE FROM advocate.magazine_issue')
        db.commit()

    with get_con() as (db, cursor):
        cursor.execute('SELECT vid, title, body, teaser FROM node_revisions')
        all_nodes = cursor.fetchall()
        # Iterate over all node_revisions
        for row in all_nodes:
            vid = row[0]
            title = row[1]
            content = row[2]

            print 'DEBUG: Processing node_revision #%s (%s)' % (vid, title)

            details = {
                'body': content,
                'title': title
            }

            # Get "key/value pairs" associated with this node_revision.
            # We're only interested in Archive, Section, and Author
            cursor.execute('''\
                SELECT vocabulary.name, term_data.name
                FROM node_revisions, term_node, term_data, vocabulary
                WHERE node_revisions.vid=term_node.vid
                    AND term_node.tid=term_data.tid
                    AND term_data.vid=vocabulary.vid
                    AND node_revisions.vid=%s
            ''', (vid,))

            details_raw = cursor.fetchall()

            # Add key/value pairs to the details dict
            for detail_raw in details_raw:
                key = detail_raw[0]
                value = detail_raw[1]
                if key not in details:
                    details[key] = []
                details[key].append(value)

            # Skip if there's more than on Archive or Section
            if warn_one(vid, title, details, 'Archive'):
                continue
            else:
                details['Archive'] = details['Archive'][0]
            if warn_one(vid, title, details, 'Section'):
                continue
            else:
                details['Section'] = details['Section'][0]

            if 'Author' not in details:
                print ('WARNING: No %ss for node_revision #%s (%s); skipping' %
                       ('Author', vid, title))
                continue

            # Add subtitle
            details['subtitle'] = get_from_table(
                cursor,
                'content_field_subtitle1',
                'field_subtitle1_value',
                vid)[0]

            # Add teaser
            details['teaser'] = get_from_table(
                cursor,
                'content_field_front_page_teaser',
                'field_front_page_teaser_value',
                vid)[0]

            # Add misc data
            details['medium'] = get_from_table(
                cursor,
                'content_field_medium',
                'field_medium_value',
                vid)[0]

            details['size'] = get_from_table(
                cursor,
                'content_field_size',
                'field_size_value',
                vid)[0]

            details['statement'] = get_from_table(
                cursor,
                'content_field_statement',
                'field_statement_value',
                vid)[0]

            for k in ('subtitle', 'teaser', 'medium', 'size', 'statement'):
                details[k] = '' if details[k] is None else details[k]

            # Get images
            fid = get_from_table(cursor, 'content_type_art', 'field_image_fid',
                                 vid)[0]
            if fid is not None:
                cursor.execute('''
                    SELECT filepath FROM files
                    WHERE fid=%s
                ''' % fid)
                details['file_path'] = cursor.fetchall()[0][0]

                if details['Section'] != 'Art':
                    print ('WARNING: node_revision #%s (%s) in '
                           '%s section but has image'
                           % (vid, title, details['Section']))

            # Actually insert node into new db schema
            insert_node(cursor, details)
            db.commit()


# Inserts a piece of content defined by the dict 'details' into the new schema
def insert_node(cursor, details):
    # Get issue and section ids
    issue_id = get_id(cursor, 'issue', 'name', details['Archive'])
    section_id = get_id(cursor, 'section', 'name', details['Section'])

    slug = re.sub(r'[^0-9a-zA-Z \-]', '',
                  details['title']).replace(' ', '-')[:99]

    # Insert content
    cursor.execute('''
        INSERT INTO advocate.magazine_content
        (title, subtitle, slug, teaser, body, medium, size, statement, issue_id,
            section_id) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (details['title'], details['subtitle'], slug, details['teaser'],
          details['body'], details['medium'], details['size'],
          details['statement'], issue_id, section_id))

    content_id = cursor.lastrowid

    # Insert visual/written content
    if 'file_path' in details:
        cursor.execute('''
            INSERT INTO advocate.magazine_image (content_ptr_id, photo)
            VALUES (%s, %s)
        ''', (content_id, details['file_path']))
    else:
        cursor.execute('''
            INSERT INTO advocate.magazine_article (content_ptr_id, photo)
            VALUES (%s, %s)
        ''', (content_id, None))

    # Add contributors
    for contributor_name in details['Author']:
        contributor_id = get_id(cursor, 'contributor', 'name', contributor_name)
        cursor.execute('''
            INSERT INTO advocate.magazine_content_contributors
                (content_id, contributor_id)
            VALUES (%s, %s)
        ''', (content_id, contributor_id))


# returns True if len(details[key]) == 1
def warn_one(vid, title, details, key):
        if key not in details:
            print ('WARNING: No %ss for node_revision #%s (%s)' %
                   (key, vid, title))
            return True

        if len(details[key]) > 1:
            print ('WARNING: %s %ss for node_revision #%s (%s)' %
                   (len(details[key]), key, vid, title))
            return True

        return False


def get_from_table(cursor, tablename, column, vid):
    cursor.execute('''
        SELECT %s FROM %s WHERE vid = %s;
    ''' % (column, tablename, vid))
    res = [r[0] for r in cursor.fetchall()]

    if not res:
        return [None]
    return res


# Gets the id of the row in tablename whose column 'column' has value 'value'
# If no matching row exists, creates a new row and returns the new row's id
def get_id(cursor, tablename, column, value):
    row_id = 0
    cursor.execute('''
        SELECT id FROM advocate.magazine_%s
        WHERE %s=%s
    ''' % (tablename, column, '%s'), (value,))
    results = cursor.fetchall()
    if results:
        row_id = results[0][0]
    else:
        if tablename != 'issue':
            cursor.execute('''
                INSERT INTO advocate.magazine_%s (%s)
                VALUES (%s)
            ''' % (tablename, column, '%s'), (value,))
        else:
            cursor.execute('''
                INSERT INTO advocate.magazine_issue (name, pub_date,
                           cover_image, theme, issue, year)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (value, date.today(), None, None, 'Fall', 2015))
        row_id = cursor.lastrowid

    return row_id


@contextmanager
def get_con():
    con = MySQLdb.connect('localhost', 'root', '', 'advocate_old')
    cursor = con.cursor()
    yield (con, cursor)
    cursor.close()
    con.close()


if __name__ == '__main__':
    main()

import os
import app as flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

    def test_edit_autofill(self):
        self.app.post('/add', data=dict(
            title='<Hello>',
            text='text',
            category='A category'
        ), follow_redirects=True)
        rv = self.app.post('/editing', data=dict(
            id='1'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'text' in rv.data
        assert b'A category' in rv.data

    def test_edit(self):
        self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        self.app.post('/editing', data=dict(
            id='1'
        ), follow_redirects=True)
        rv = self.app.post('/edit_entry', data=dict(
            id='1',
            title='HELLO',
            text='New text',
            category='New category'
        ), follow_redirects=True)
        assert b'Entry was successfully updated' in rv.data
        assert b'HELLO' in rv.data
        assert b'New text' in rv.data
        assert b'New category' in rv.data
        assert b'&lt;Hello&gt;' not in rv.data

    def test_delete(self):
        self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        rv = self.app.post('/delete_entry', data=dict(
            id='1'
        ), follow_redirects=True)
        assert b'Entry was successfully deleted' in rv.data
        assert b'&lt;Hello&gt;' not in rv.data
        assert b'<strong>HTML</strong> allowed here' not in rv.data
        assert b'A category' not in rv.data

    def test_filter(self):
        self.app.post('/add', data=dict(
            title='Original title',
            text='Original text',
            category='Category'
        ), follow_redirects=True)
        self.app.post('/add', data=dict(
            title='Different title',
            text='Different text',
            category='Category2'
        ), follow_redirects=True)
        rv = self.app.get('/?filter=Category2')
        assert b'Different title' in rv.data
        assert b'Original title' not in rv.data
        assert b'Different text' in rv.data
        assert b'Original text' not in rv.data

    def test_undo_filter(self):
        self.app.post('/add', data=dict(
            title='Title1',
            text='Text1',
            category='Category1'
        ), follow_redirects=True)
        self.app.post('/add', data=dict(
            title='Title2',
            text='Text2',
            category='Category2'
        ), follow_redirects=True)
        self.app.get('/?filter=Category2')
        rv = self.app.get('/')
        assert b'Title1' in rv.data
        assert b'Title2' in rv.data
        assert b'Text1' in rv.data
        assert b'Text2' in rv.data
        assert b'Category1' in rv.data
        assert b'Category2' in rv.data

if __name__ == '__main__':
    unittest.main()
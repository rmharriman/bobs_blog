import threading
import unittest
from selenium import webdriver
from app import db, create_app
from app.models import User, Role, Post

class SeleniumTestCase(unittest.TestCase):
    client = None
    
    # setup and tearDown class are invoked before and after the tests in 
    # this class execute
    @classmethod
    def setUpClass(cls):
        # start Firefox
        try:
            cls.client = webdriver.Firefox()
        except:
            pass
        
        # skip these tests if the browser could not start
        if cls.client:
            # create the application
            cls.app = create_app("testing")
            cls.app_context = cls.app.app_context()
            cls.app_context.push()
            
            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger("werkzeug")
            logger.setLevel("ERROR")
            
            # create the database and populate with some fake data
            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generaate_fake(10)
            
            # add an admin user
            admin_role = Role.query.filter_by(permission=0xff).first()
            admin = User(email="jonh@example.com",
                         username="john",
                         password="cat",
                         roel=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()
            
            # start the Flask server in a thread
            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the flask server and the browser
            cls.client.get("http://localhost:5000/shutdown")
            cls.client.close()
            
            # destroy database
            db.drop_all()
            db.session.remove()
            
            # remove application context
            cls.app_context.pop()
            
    def setUp(self):
        if not self.client:
            self.skipTest("Web browser not available")
        
    def tearDown(self):
        pass
        
    def test_home_page(self):
        # navigate to home page
        self.client.get("http://localhost:5000/")
        self.assertTrue(re.search("Hello,\s+Stranger!", self.client.page_source))
        
        # navigate to the login page
        self.client.find_element_by_link_text("Log In").click()
        self.assertTrue("<h1>Login</h1>" in self.client.page_source)
        
        # login
        self.client.find_element_by_name("email").send_keys("john@example.com")
        self.client.find_element_by_name("password").send_keys("cat")
        self.client.find_element_by_name("submit").click()
        self.assertTrue(re.search("Hello,\s+john!", self.client.page_source))
        
        # navigate to the user's profile page
        self.client.find_element_by_link_text("Profile").click()
        self.assertTrue("<h1>Login</h1>" in self.client.page_source)

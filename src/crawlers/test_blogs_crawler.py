"""
Test script for BlogsCrawler
This script tests the simplified BlogsCrawler functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_blog_item_creation():
    """Test BlogItem creation"""
    print("Testing BlogItem creation...")
    
    try:
        from data_models import BlogItem
        
        # Create a test blog item
        blog_item = BlogItem(
            id="test-123",
            title="Test Blog Post",
            url="https://example.com/blog/test",
            published_date="2025-01-18T10:00:00",
            description="This is a test blog post description.",            
            tags="testing, blog, example"
        )
        
        # Convert to dict and back
        blog_dict = blog_item.to_dict()
        print(f"Blog item dict: {blog_dict}")
        
        # Create from dict
        blog_item_from_dict = BlogItem.from_dict(blog_dict)
        print(f"Recreated blog item title: {blog_item_from_dict.title}")
        
        return True
        
    except Exception as e:
        print(f"Error testing BlogItem creation: {e}")
        return False

def test_blogs_crawler_initialization():
    """Test BlogsCrawler initialization"""
    print("\nTesting BlogsCrawler initialization...")
    
    try:
        from blogs_crawler import BlogsCrawler
        
        # Mock services for testing
        class MockCosmosDBService:
            def upsert_item(self, item, container_name):
                print(f"Mock: Would save item {item['id']} to container {container_name}")
                return item
        
        class MockFoundryService:
            def generate_embedding(self, text):
                print(f"Mock: Would generate embedding for text length: {len(text)}")
                return [0.1, 0.2, 0.3]  # Mock embedding
        
        # Initialize BlogsCrawler with mock services
        cosmos_service = MockCosmosDBService()
        foundry_service = MockFoundryService()
        
        crawler = BlogsCrawler(cosmos_service, foundry_service)
        print("BlogsCrawler initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"Error testing BlogsCrawler initialization: {e}")
        return False

def test_blog_item_processing():
    """Test BlogItem processing"""
    print("\nTesting BlogItem processing...")
    
    try:
        from blogs_crawler import BlogsCrawler
        from data_models import BlogItem
        
        # Mock services
        class MockCosmosDBService:
            def upsert_item(self, item, container_name):
                print(f"Mock: Saved item '{item['title']}' to container '{container_name}'")
                return item
        
        class MockFoundryService:
            def generate_embedding(self, text):
                return [0.1, 0.2, 0.3, 0.4, 0.5]  # Mock embedding
        
        # Create test blog item
        blog_item = BlogItem(
            id="test-456",
            title="Another Test Post",
            url="https://example.com/blog/another-test",
            published_date="2025-01-18T11:00:00",
            description="Another test description.",            
            tags="testing, example"
        )
        
        # Initialize and test
        crawler = BlogsCrawler(MockCosmosDBService(), MockFoundryService())
        crawler.process_blog_item(blog_item)
        
        print("Blog item processed successfully")
        return True
        
    except Exception as e:
        print(f"Error testing blog item processing: {e}")
        return False

if __name__ == "__main__":
    print("Running simplified BlogsCrawler tests...")
    
    # Test BlogItem creation
    blog_item_test_passed = test_blog_item_creation()
    
    # Test BlogsCrawler initialization
    crawler_init_test_passed = test_blogs_crawler_initialization()
    
    # Test blog item processing
    processing_test_passed = test_blog_item_processing()
    
    # Summary
    print(f"\n{'='*50}")
    print("Test Results:")
    print(f"BlogItem creation: {'PASSED' if blog_item_test_passed else 'FAILED'}")
    print(f"BlogsCrawler initialization: {'PASSED' if crawler_init_test_passed else 'FAILED'}")
    print(f"Blog item processing: {'PASSED' if processing_test_passed else 'FAILED'}")
    
    if blog_item_test_passed and crawler_init_test_passed and processing_test_passed:
        print("\nAll tests passed! Simplified BlogsCrawler is ready to use.")
    else:
        print("\nSome tests failed. Please check the errors above.")

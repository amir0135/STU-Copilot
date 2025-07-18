from typing import Dict, Optional

class BlogItem:
    """Data class to hold blog post information"""

    def __init__(self, id: str, title: str, url: str, published_date: str,
                 description: Optional[str] = None, tags: Optional[str] = None,
                 embedding: Optional[float] = None):
        self.id = id  # Unique identifier for the blog post
        self.title = title
        self.url = url
        self.description = description
        self.tags = tags
        self.published_date = published_date
        self.embedding = embedding

    def to_dict(self) -> Dict:
        """Convert the blog item to a dictionary for saving to CosmosDB"""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "description": self.description,            
            "tags": self.tags,
            "published_date": self.published_date,
            "embedding": self.embedding
        }

    @staticmethod
    def from_dict(data: Dict) -> 'BlogItem':
        """Create a BlogItem instance from a dictionary"""
        return BlogItem(
            id=data.get("id"),
            title=data.get("title"),
            url=data.get("url"),
            description=data.get("description"),            
            tags=data.get("tags"),
            published_date=data.get("published_date"),
            embedding=data.get("embedding")
        )

class RepositoryInfo:
    """Data class to hold repository information"""

    def __init__(self, id: str, organization: str, name: str, url: str,
                 updated_at: str, stars_count: int, archived: bool,
                 description: Optional[str] = None, tags: Optional[str] = None,
                 embedding: Optional[float] = None):
        self.id = id  # Unique identifier for the repository
        self.organization = organization
        self.name = name
        self.url = url
        self.description = description
        self.tags = tags
        self.updated_at = updated_at
        self.stars_count = stars_count
        self.archived = archived
        self.embedding = embedding

    def to_dict(self) -> Dict:
        """Convert the repository info to a dictionary for saving to CosmosDB"""
        return {
            "id": self.id,
            "organization": self.organization,
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "tags": self.tags,
            "updated_at": self.updated_at,
            "stars_count": self.stars_count,
            "archived": self.archived,
            "embedding": self.embedding
        }

    @staticmethod
    def from_dict(data: Dict) -> 'RepositoryInfo':
        """Create a RepositoryInfo instance from a dictionary"""
        return RepositoryInfo(
            id=data.get("id"),
            organization=data.get("organization"),
            name=data.get("name"),
            url=data.get("url"),
            description=data.get("description"),
            tags=data.get("tags"),
            updated_at=data.get("updated_at"),
            stars_count=data.get("stars_count", 0),
            archived=data.get("archived", False),
            embedding=data.get("embedding")
        )
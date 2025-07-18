from typing import Dict, Optional

class RepositoryInfo:
    """Data class to hold repository information"""

    def __init__(self, id: str, organization: str, name: str, url: str,
                 updated_at: str, stars_count: int, archived: bool,
                 description: Optional[str] = None, keywords: Optional[str] = None,
                 embedding: Optional[float] = None):
        self.id = id  # Unique identifier for the repository
        self.organization = organization
        self.name = name
        self.url = url
        self.description = description
        self.keywords = keywords
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
            "keywords": self.keywords,
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
            keywords=data.get("keywords"),
            updated_at=data.get("updated_at"),
            stars_count=data.get("stars_count", 0),
            archived=data.get("archived", False),
            embedding=data.get("embedding")
        )
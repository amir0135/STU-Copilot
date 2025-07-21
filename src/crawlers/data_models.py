from typing import Dict, Optional
from datetime import datetime


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


class SeismicContent:
    """Data class to hold Seismic content information"""

    @staticmethod
    def _to_iso_date(date_str: str) -> str:
        if not date_str or not isinstance(date_str, str):
            return date_str
        try:
            # Example: 'Jul 18, 2025 at 11:26 PM'
            dt = datetime.strptime(date_str, "%b %d, %Y at %I:%M %p")
            return dt.isoformat() + 'Z'
        except Exception:
            return date_str

    def __init__(self, id: str, name: str, url: str, version: str, versionCreatedDate: str, publishTime: str, createTime: str,
                 expirationDate: str, description: str, size: str, format: str, Confidentiality: str, Sales_Stage: str,
                 Audience: str, Competitor: str, Level: str, Language: str, Industry: str, Initiative: str, Segment: str,
                 Content_Sub_Type: str, Industry_Sub_Vertical: str, Solution_Area: str, Content_Group: str, Products: str,
                 Solution_Play: str, Industry_Vertical: str, embedding: Optional[float] = None):
        self.id = id
        self.name = name
        self.url = url
        self.version = version
        self.version_created_date = self._to_iso_date(versionCreatedDate)
        self.publish_time = self._to_iso_date(publishTime)
        self.create_time = self._to_iso_date(createTime)
        self.expiration_date = self._to_iso_date(expirationDate)
        self.description = description
        self.size = size
        self.format = format
        self.confidentiality = confidentiality
        self.sales_stage = sales_stage
        self.audience = audience
        self.competitor = competitor
        self.level = level
        self.language = language
        self.industry = industry
        self.initiative = Initiative
        self.segment = Segment
        self.content_sub_type = Content_Sub_Type
        self.industry_sub_vertical = Industry_Sub_Vertical
        self.solution_area = Solution_Area
        self.content_group = Content_Group
        self.products = Products
        self.solution_play = Solution_Play
        self.industry_vertical = Industry_Vertical
        self.embedding = embedding

    def to_dict(self) -> Dict:
        """Convert the SeismicContent to a dictionary for saving to CosmosDB"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "version": self.version,
            "versionCreatedDate": self.versionCreatedDate,
            "publishTime": self.publishTime,
            "createTime": self.createTime,
            "expirationDate": self.expirationDate,
            "description": self.description,
            "size": self.size,
            "format": self.format,
            "Confidentiality": self.Confidentiality,
            "Sales Stage": self.Sales_Stage,
            "Audience": self.Audience,
            "Competitor": self.Competitor,
            "Level": self.Level,
            "Language": self.Language,
            "Industry": self.Industry,
            "Initiative": self.Initiative,
            "Segment": self.Segment,
            "Content Sub-Type": self.Content_Sub_Type,
            "Industry Sub-Vertical": self.Industry_Sub_Vertical,
            "Solution Area": self.Solution_Area,
            "Content Group": self.Content_Group,
            "Products": self.Products,
            "Solution Play": self.Solution_Play,
            "Industry Vertical": self.Industry_Vertical,
            "embedding": self.embedding
        }

    @staticmethod
    def from_dict(data: Dict) -> 'SeismicContent':
        """Create a SeismicContent instance from a dictionary"""
        return SeismicContent(
            id=data.get("id"),
            name=data.get("name"),
            url=data.get("url"),
            version=data.get("version"),
            versionCreatedDate=SeismicContent._to_iso_date(
                data.get("versionCreatedDate")),
            publishTime=SeismicContent._to_iso_date(data.get("publishTime")),
            createTime=SeismicContent._to_iso_date(data.get("createTime")),
            expirationDate=SeismicContent._to_iso_date(
                data.get("expirationDate")),
            description=data.get("description"),
            size=data.get("size"),
            format=data.get("format"),
            Confidentiality=data.get("Confidentiality"),
            Sales_Stage=data.get("Sales Stage", "--"),
            Audience=data.get("Audience"),
            Competitor=data.get("Competitor", "--"),
            Level=data.get("Level"),
            Language=data.get("Language"),
            Industry=data.get("Industry", "--"),
            Initiative=data.get("Initiative", "--"),
            Segment=data.get("Segment"),
            Content_Sub_Type=data.get("Content Sub-Type"),
            Industry_Sub_Vertical=data.get("Industry Sub-Vertical", "--"),
            Solution_Area=data.get("Solution Area"),
            Content_Group=data.get("Content Group"),
            Products=data.get("Products", "--"),
            Solution_Play=data.get("Solution Play", "--"),
            Industry_Vertical=data.get("Industry Vertical", "--"),
            embedding=data.get("embedding")
        )

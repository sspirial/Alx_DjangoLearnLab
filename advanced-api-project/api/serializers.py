from rest_framework import serializers
from datetime import date
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    """
    Custom serializer for the Book model.
    
    This serializer handles the serialization and deserialization of Book instances,
    including custom validation to ensure the publication year is not in the future.
    
    Features:
    - Serializes all fields of the Book model (title, publication_year, author)
    - Includes custom validation for publication_year
    - Provides clear error messages for validation failures
    - Handles foreign key relationships properly
    
    Validation Rules:
    - publication_year must not be in the future (cannot exceed current year)
    """
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author']
    
    def validate_publication_year(self, value):
        """
        Custom validation method for the publication_year field.
        
        Ensures that the publication year is not in the future by comparing
        it with the current year. This prevents data inconsistencies and
        maintains logical integrity of the book records.
        
        Args:
            value (int): The publication year to validate
            
        Returns:
            int: The validated publication year
            
        Raises:
            serializers.ValidationError: If publication year is in the future
        """
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. "
                f"Current year is {current_year}, but got {value}."
            )
        return value
    
    def validate(self, data):
        """
        Object-level validation method.
        
        Performs additional validation that may involve multiple fields.
        Can be extended to include cross-field validation rules.
        
        Args:
            data (dict): Dictionary containing all field values
            
        Returns:
            dict: The validated data dictionary
        """
        # Additional validation can be added here if needed
        # For example, checking if title and author combination already exists
        return data


class AuthorSerializer(serializers.ModelSerializer):
    """
    Custom serializer for the Author model with nested Book serialization.
    
    This serializer provides a comprehensive representation of authors including
    their associated books through nested serialization. It demonstrates advanced
    DRF features for handling one-to-many relationships.
    
    Features:
    - Includes author's basic information (name)
    - Dynamically serializes all related books using nested BookSerializer
    - Uses the 'books' related_name from the Author-Book relationship
    - Provides read-only access to nested books (books are managed separately)
    - Maintains referential integrity through proper relationship handling
    
    Relationship Handling:
    The 'books' field uses the related_name='books' defined in the Book model's
    foreign key to Author. This creates a reverse relationship that allows
    accessing all books by a specific author. The nested serialization provides
    complete book details within the author representation.
    """
    
    # Nested serialization of related books
    # Uses the related_name='books' from the Book model's author ForeignKey
    books = BookSerializer(many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books']
    
    def validate_name(self, value):
        """
        Custom validation method for the name field.
        
        Ensures the author name meets basic quality requirements such as
        proper length and format validation.
        
        Args:
            value (str): The author name to validate
            
        Returns:
            str: The validated author name
            
        Raises:
            serializers.ValidationError: If name doesn't meet requirements
        """
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Author name must be at least 2 characters long."
            )
        
        # Check if name contains only letters, spaces, hyphens, and apostrophes
        import re
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", value):
            raise serializers.ValidationError(
                "Author name can only contain letters, spaces, hyphens, apostrophes, and periods."
            )
        
        return value.strip()
    
    def to_representation(self, instance):
        """
        Override the default representation to customize output format.
        
        This method allows customization of how the serialized data appears
        in API responses. It can be used to add computed fields, format data,
        or modify the structure of the output.
        
        Args:
            instance (Author): The Author model instance being serialized
            
        Returns:
            dict: The customized representation dictionary
        """
        representation = super().to_representation(instance)
        
        # Add a computed field showing the total number of books by this author
        representation['books_count'] = len(representation['books'])
        
        # Add the most recent publication year if author has books
        if representation['books']:
            latest_year = max(book['publication_year'] for book in representation['books'])
            representation['latest_publication_year'] = latest_year
        else:
            representation['latest_publication_year'] = None
        
        return representation


class AuthorDetailSerializer(serializers.ModelSerializer):
    """
    Simplified Author serializer without nested books for list views.
    
    This serializer provides a lightweight representation of authors without
    the nested book data, which is more efficient for list views where
    detailed book information is not needed.
    
    Use Cases:
    - Author list endpoints where performance is important
    - Dropdown selections or reference fields
    - Scenarios where only author basic info is needed
    """
    
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books_count']
    
    def get_books_count(self, obj):
        """
        Method field to get the count of books by this author.
        
        This provides the book count without serializing all book details,
        making it efficient for list views while still providing useful
        summary information.
        
        Args:
            obj (Author): The Author model instance
            
        Returns:
            int: Number of books by this author
        """
        return obj.books.count()
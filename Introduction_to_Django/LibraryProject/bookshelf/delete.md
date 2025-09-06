# Delete Operation
First, import the `Book` model at the top of your Python file:

```python
from bookshelf.models import Book

book = Book.objects.get(title='Nineteen Eighty-Four')
book.delete()
print(Book.objects.all())
# Output: <QuerySet []>
```

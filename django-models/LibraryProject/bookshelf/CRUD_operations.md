# CRUD Operations Documentation

## Create
```python
book = Book.objects.create(title='1984', author='George Orwell', publication_year=1949)
# Output: <Book: 1984 by George Orwell (1949)>
```

## Retrieve
```python
book = Book.objects.get(title='1984')
print(book.title, book.author, book.publication_year)
# Output: 1984 George Orwell 1949
```

## Update
```python
book = Book.objects.get(title='1984')
book.title = 'Nineteen Eighty-Four'
book.save()
print(book.title)
# Output: Nineteen Eighty-Four
```

## Delete
```python
book = Book.objects.get(title='Nineteen Eighty-Four')
book.delete()
print(Book.objects.all())
# Output: <QuerySet []>
```

# Managing Pydantic Data Models in FastAPI

## Defining models and their filed types with Pydantic

Pydantic is a powerful library for defining data models using Python classes and type hints. This approach makes those classes completly compatible with static type checking. Besides, since there are regular Python classes, we can use inheritance and also define our very own methods to add custom logic. 

### Standard field types

We'll begin by defining fields with standard type, which only involves simple type hints. Let's review a simple model representing information about a person. You can see this in the following code example:

```python
from pydantic import BaseModel

class Person(BaseModel):
    first_name:str
    last_name:str
    age:int
```

Also you're not limited to scalar types: we can actually use compound types such as lists, tuples, or datetime classes. In the following example, you can see a model using those more complex types:

```python
from datetime import date
from enum import Enum
from typing import List

from pydantic import BaseModel, ValidationError

class Gender(srt, Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    NON_BINARY = 'NON_BINARY'

class Person(BaseModel):
    first_name:str
    last_name:str
    gender: Gender
    birthdate: date
    interests: List[str]
```

That's not all, fields can be Pydantic models themselves, allowing you to have sub-objects:

```python

class Address(BaseModel):
    street_address: str
    postal_code: str
    city: str
    country: str

class Person(BaseModel):
    first_name:str
    last_name:str
    gender: Gender
    birthdate: date
    interests: List[str]
    address: Address
```

### Optional fields and default values

Up to now, we've assumed that each field had to be provided when instantiating the model. Quite often there are values that we want to be optional because they may not be relevant for each object instance. Sometimes, we also wish to set a default value for a field when it's not specified. 

As you may guessed, this is done quite simply, with the Optional typing annotation:

```python
from typing import Optional

from pydantic import BaseModel

class UserProfile(BaseModel):
    nickname: str
    location: Optional[str] = None
    subscribed_newsletter: bool = True

user = UserProfile(nickname='jdoe')
print(user)
```

If you need to assign dynamic default values, pydantic provides Field function that allows us to set some advanced options on our fields, including one to set a factory for creating dynamic values. 


### Field validation:

In chapter 3, was showed how to apply some validation to the request parameters to check if a number was in a certain range or if string was matching regular expression (regex). We can apply the same ones to apply validation to the fields of a model.

To do this, we use the **Field** function from pydantic

```python
from typing import Optional

from pydantic import BaseModel, Field, ValidationError

class Person(BaseModel):
    first_name: str = Field(...,min_lenght=3)
    last_name: str = Field(..., min_lenght=3)
    age: Optional[int] = Field(None, ge=0,le=120)
```

You can view a complete list of the arguments accepted by **Field** in the official pydantic [documentation](https://pydantic-docs.helpmanual.io/usage/schema/#field-customisation)


### Dynamic default values

Pydantic also provides the **default_factory** argument on the **Field** function to cover this use case. This argument expects you to pass a function that will be called during model instantiation. Thus the resulting object will be evaluated at runtime each time you create a new object. 

```python
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

def list_factory():
    return ['a','b','c']

class Model(BaseModel):
    l: List[str] = Field(default_factory=list_factory)
    d: datetime = Field(default_factory=datetime.now)
    l2: List[str] = Filed(default_factory=list)
```

### Validating email addresses and URLs with Pydantic types


For convenience, pydantic provides some classes to use as field types to validate some common patterns such as email addresses or Uniform Resource Locators(URL)


```python
from pydantic import BaseModel, EmailStr, HttpUrl, ValidationError

class User(BaseModel):
    email: EmailStr
    website: HttpUrl

```

There are also other types that might be useful in the [documentation](https://pydantic-docs.helpmanual.io/usage/types/#pydantic-types)


### Creating model variations which class inheritance

```python
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str

class PostPublic(BaseModel):
    id: int
    title: str
    content: str

class PostDB(BaseModel):
    id: int
    title: str
    content: str
    nb_views: int = 0

```

We have three models here, covering three situations. These are outlined as follows:

- PostCreate: will be used for a POST endpoint to create a new post. We expect the user to give the title and the content; however, the identifier(ID), will be automatically determined by the database.
- PostPublic: will be used when we retrieve the data of a post. We want its title and content, of course, but also its associated ID in the database.
- PostDB: will carry all the data we wish to store in the database. Here, we also want to store the number of views, but we want to keep this secret to make our own statistics internally. 


Here we are repeating a lot, a solution here is to leverage model inheritance to avoid this. The approach is simple: identify the fields that are common to every variation and put them in a model that will be used as base for every other. 


```python
from pydantic import BaseModel

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostPublic(PostBase):
    id: int

class PostDB(PostBase):
    id: int
    nb_views: int = 0

```

This is also useful when you want to define methods on your model. Remember that pydantic models are regular python classes, so you can implement as many methods as you wish!

```python
class PostBase(BaseModel):
    title: str
    content: str

    def excerpt(sefl) -> str:
        return f'{self.content[:140]}...'
```

## Adding Custom data validation with Pydantic

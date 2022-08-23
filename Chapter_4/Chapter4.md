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

Probably in a real world project, you might need to add your own custom validation logic for your specific case. Pydantic allows this by defining validator, which are methods on the model that can be applied at a field lever or an object level. 

### Applying validation at a field level

This is the most common case: have a validation rule for a single field. To define it in pydantic, we'll just have to write a static method on our model and decorate it with the validator. As a reminder, decorators are syntatic sugar, allowing the wrapping of a function or a class with common logic, without compromising redability. 

```python
from datetime import date

from pydantic import BaseModel, validator

class Person(BaseModel):
    first_name: str
    last_name: str
    birthdate: date

    @validator
    def valid_birthdate(cls, v:date):
        delta = date.today() - v
        age = delta.days / 365
        if age > 120:
            raise ValueError("You seem a bit too old!")
        return v
```

As you see the validator is a static class method, with the value to validate v as the argument. It's decorated by the validator decorator, which expects the name of the arguments to validate as the first argument.
Pydantic expects two things for this method, detailed as follows:
- If the value is not valid according to your logic, you should raise a *ValueError* error with an explicit error message.
- Otherwise, you should return the value that will be assigned in the model. Notice that it doesn't need to be tha same as the input value: you can very well change it to fit your needs. That's actually what we'll do in an upcoming section. *Applying validation before Pydantic parsing.*

### Applying validation at an object level

It happens quite often that the validation of one field is dependent on another -for example, to check if a password confirmation matches the password or to enforce a filed to be required in a certain circumstances. To allow this kind of validation, we need to to access to whole object data. For this, pydantic provides the *root_validator* decorator:

```python
from pydantic import BaseModel, EmailStr, ValidationError, root_validator

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    password_confirmation: str

    @root_validator()
    def passwords_match(cls, values):
        password = values.get("password")
        password_confirmation = values.get("password_confirmation")
        if password != password_confirmation:
            raise ValueError("Passwords don't match")
        return values
```

### Applying validation before Pydantic parsing

By default your validators are run after parsing pydantic has done its parsing work. This means that the value you get already conforms to the type of the field you specified. If the type is incorrect, pydantic raises an error without calling your validator. 

However, you may sometimes wish to provide some custom parsing logic that allows you to transform input values that would have been incorrect for the type you set. In that case, you would need to run your validator before the pydantic parser: this is the purpose of the **pre** argument on **validator**.

```python
from typing import List

from pydantic import BaseModel, validator

class Model(BaseModel):
    values: List[int]

    @validator("values", pre=True)
    def split_string_values(cls, v):
        if isintance(v,str):
            return v.split(",")
        return v

m = Model(value='1,2,3')
```

## Working with Pydantic objects

When developing API endpoints with FastAPI, you'll likely get a lot of Pydantic models instances to handle. It's then up to you to implement the logic to make a link between those objects and your services, such as your database or your machine learning (ML) model. Fortunately, Pydantic provides methods to make this very easy. We'll review common use cases that will be useful for you during development. 

### Converting an object into a dictionary

This is probably the action you'll perform most on a pydantic object: covert it to a raw dictionary that'll be easy to send another API or use case in a database, for example. You just have to call the dict method on the object instance:

```python
person = Person(
    first_name = 'John',
    last_name = 'Doe',
    gender = Gender.MALE,
    birthdate = "1991-01-01",
    interest = ["travel","sports"],
    address = {
        "street_address":"12 Squirell Street",
        "postal_code":"424242",
        "city":"Woodtown",
        "country":"US",}
)

person_dict = person.dict()
print(person_dict['first_name'])
print(person_dict["address"]["street_address"])
```

Also you can add some arguments, allowing to select a subset of properties to be converted. You can either state the ones you want to be included or the ones you want to exclude:


```python
person_includes = person.dict(include={"first_name", "last_name"})
print(person_includes)

person_excludes = person.dict(exclude={"birthdate","interests"})
```
If you use a coversion quite often, it can be interesting to put in a method so that you can reuse it at will:

```python
class Person(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    birthdate: date
    interest: List[str]
    address: Address

    def name_dict(self):
        return self.dict(include={"first", "last_name"})
```

### Creating an instance from a sub-class object

In a particular situation you'll have a model dedicated for the creation endpoint, with only the required fields for a creation, and a database model with all the fields we want to store.

```python
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

In the *path* operation function for our *create* endpoint, we'll thus get a **PostCreate** instance with only title and content. However, we need to build a proper *PostDB* instance before storing it in the database. A convient way to do this is to jointly use the dict method and the unpacking syntax. 

```python
@app.post("/posts",status_code=status.HTTP_201_CREATED,response_model=PostPublic)
async def create(post_create: PostCreate):
    new_id = max(db.post.keys() or (0,1))+1
    post = PostDB(id=new_id, **post_create.dict())
    db.post[new_id] = post
    return post
```
### Updating an instance with a partial one

In some situations you'll want to allow partial updates. In other words you'll allow the end user to only send the fields they want to change to your API and omit the ones that shouldn't change. This is the usual way of implementing a **PATCH** endpoint. 

To do this, you would first need a special Pydantic model with all fields marked as a optional so that no error es raised when a field is missing. 


```python
class PostBase(BaseModel):
    title: str
    content: str

class PostPartialUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
```

We are now able to implement an endpoint that will accept a subset of our Post fields. Since it's an update, we'll retrieve an existing post in the database thanks to its ID. Then, we'll have to find a way to only update the fields in the payload and keep the others untouched. Fortunately, Pydantic once again has this covered, with a handy methods and options.

```python
@app.patch("/posts/{id}",response_model=PostPublic)
async def partial_update(id: int, post_update: PostPartialUpdate):
    try:
        post_db = db.posts[id]
        updated_fields = post_update.dict(exclude_unset=True)
        updated_post = post_db.copy(update=updated_fields)

        db.posts[id] = updated_post
        return updated_post
    except KeyError:
        raise HTTPException(status.HTTP_404_NOT_FOUND)        

```



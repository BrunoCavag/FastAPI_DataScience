# Developing a RESTful API with FastAPI

## Creating the first endpoint and running it locally 

```python 
from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def hello_world():
    return {"hello":"world"}
```
The to run it, need a web server compatible with fastapi, in this case uvicorn.

```bash
uvicorn *name_of_script:app

```
And you can also interect with a fastAPI interactive userinterface:

![image](/notes_screenshots/fastapi_swagger.png)

## Handeling request parameters:

The main goal of a REST API is to provide a structured way in which to interact with data.
As such, it's crucial for the end user to send some information to tailor the response they
need, such as path parameters, query parameters, body payloads, or headers.

To handle them, usually, web frameworks ask you to manipulate a request object to
retrieve the parts you are interested in and manually apply validation. However, that's
not necessary with FastAPI! Indeed, it allows you to define all of your parameters
declaratively. Then, it'll automatically retrieve them in the request and apply validations
based on the type hints.

Next, we'll explore how you can use this feature to retrieve and validate this input data
from different parts of the request.

### Path parameters

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{id}")
async def get_user(id:int):
    return {"id": id}
```

### Limiting allowed values:

So, what if we just want to accept a limited set of values? Once again, we'll lean on type
hinting. Python has a very useful class for this: Enum. An enumeration is a way to list
all the valid values for a specific kind of data. Let's define an Enum class that will list the
different types of users:

```python
from enum import Enum
from fastapi import FastAPI

class UserType(str, Enum):
    STANDARD = "standard"
    ADMIN = "admin"

```

To define a string enumeration, we inherit from both the str type and the Enum class.
Then, we simply list the allowed values as class properties: the property name and its
actual string value. Finally, we need to type hint the type argument using this class:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{type}/{id}")
async def get_user(type: UserType,id:int):
    return {"type":type,"id": id}
```

### Advance Validation:

We can take one step further by defining more advanced validation rules, particularly for
numbers and strings. In this case, the type of hint is no longer enough. We'll rely on the
functions provided by FastAPI, allowing us to set some options on each of our parameters.
For path parameters, the function is named Path. In the following example, we'll only
allow an id argument that is greater than or equal to 1:

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/users/{id}")
async def get_user(id:int=Path(..., ge=1)):
    return {"id": id}
```

More complex validations:

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/users/{id}")
async def get_license_plate(license:str=Path(..., min_length=9, max_length=9)):
    return {"license": license}
```

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/users/{id}")
async def get_license_plate(license:str=Path(..., regex=r"^\w{2}-\d{3}-\w{2}$")):
    return {"license": license}
```

### Query parameters:

Query parameters are a common way to add some dynamic parameters to a URL. You
find them at the end of the URL in the following form: *?param1=foo&param2=bar*.
In a REST API, they are commonly used on read endpoints to apply pagination, a filter, a
sorting order, or selecting fields.

```python
@app.get("/users")
async def get_user(page:int,size:int=10):
    return {"page": page, "size":size}
```
Here, you can see that we have defined a default value for those arguments, which means
they are optional when calling the API. Of course, if you wish to define a required query
parameter, simply leave out the default value:

```python
from enum import Enum
from fastapi import FastAPI

class UserFormat(str, Enum):
    SHORT='shor'
    FULL='full'

@app.get("/users")
async def get_user(format:UserFormat):
    return {"format":format}
```


### The request body

The body is the part of the HTTP request that contains raw data, representing documents,
files, or form submissions. In a REST API, it's usually encoded in JSON and used to create
structured objects in a database.
For the simplest cases, retrieving data from the body works exactly like query parameters.
The only difference is that you always have to use the Body function; otherwise, FastAPI
will look for it inside the query parameters by default. Let's explore a simple example
where we want to post some user data:

```python
@app.post("/users")
async def create_user(name:str = Body(...), age:int = Body(...)):
    return {"name":name, "age":age}
```

You also have access to more advanced validation through the Body function. It works in
the same way as we demonstrated in the Path parameters section.

However, defining payload validations like this has some major drawbacks. First, it's quite
verbose and makes the path operation function prototype huge, especially for bigger
models. Second, usually, you'll need to reuse the data structure on other endpoints or in
other parts of your application.

This is why FastAPI uses pydantic models for data validation. Pydantic is a Python library
for data validation and is based on classes and type hints. In fact, the Path, Query, and
Body functions that we've learned about so far use pydantic under the hood!
By defining your own pydantic models and using them as type hints in your path
arguments, FastAPI will automatically instantiate a model instance and validate the data.
Let's rewrite our previous example using this method:

```python
from fastapi import FastAPI
from pydantic import BaseModel

class User(BaseModel):
    name:str
    age: int

app = FastAPI()

@app.post("/users")
async def create_user(user: User):
    return user
```

### Multiple Objects

Sometimes, you might find that you have several objects that you wish to send in the
same payload all at once. For example, both user and company. In this scenario, you
can simply add several arguments that have been type hinted by a pydantic model, and
FastAPI will automatically understand that there are several objects. In this configuration,
it will expect a body containing each object indexed by its argument name:

```python
@app.post("users")
async def create_user(user:User, company:Company):
    return {"user":user,"company":company}
```


### Form data and file uploads

Even if REST APIs work most of the time with JSON, sometimes, you might have
to handle form-encoded data or file uploads, which have been encoded either as
application/x-www-form-urlencoded or multipart/form-data.

One drawback to this approach is that the uploaded file is entirely stored in memory. So,
while it'll work for small files, it is likely that you'll run into issues for larger files. Besides,
manipulating a bytes object is not always convenient for file handling.
To fix this problem, FastAPI provides an UploadFile class. This class will store the data
in memory up to a certain threshold and, after this, will automatically store it on disk in
a temporary location. This allows you to accept much larger files without running out of
memory. Furthermore, the exposed object instance exposes useful metadata, such as the
content type, and a file-like interface. This means that you can manipulate it as a regular
file in Python and that you can feed it to any function that expects a file.

![image](/notes_screenshots/upload_multiple_files.png)

### Headers and cookies

Besides the URL and the body, another major part of the HTTP request are the headers.
They contain all sorts of metadata that can be useful when handling requests. A common
usage is to use them for authentication, for example, via the famous cookies.

```python
@app.get("/")
async def get_header(hello:str=Header(...)):
    return {"hello":hello}
```

### The request object


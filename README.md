![Build Status](https://github.com/repobee/repobee-sanitizer/workflows/tests/badge.svg)
[![Code Coverage](https://codecov.io/gh/repobee/repobee-sanitizer/branch/master/graph/badge.svg)](https://codecov.io/gh/repobee/repobee-sanitizer)
![Supported Python Versions](https://img.shields.io/badge/python-3.6%2C%203.7%2C%203.8-blue.svg)
![Supported Platforms](https://img.shields.io/badge/platforms-Linux%2C%20macOS-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# repobee-sanitizer

A plugin for RepoBee to sanitize template repositories before being pushed to students.
`repobee-sanitizer` adds the commands `sanitize-file` and `sanitize-repo` that lets the user sanitize files and repos (directories currently) respectively.
`repobee-sanitizer` can remove or replace text by going through files, looking for certain `REPOBEE-SANITIZER-<type>` text-markers. The most simple usage consists of a `REPOBEE-SANITIZER-START` and a `REPOBEE-SANITIZER-END` marker, where content between these two markers will be removes, or "santitized".

# Example use cases

Consider the following code:

```java
class StackTest {
    @Test
    public void topIsLastPushedValue() {
REPOBEE-SANITIZER-START
        // Arrange
        int value = 1338;

        // Act
        emptyStack.push(value);
        stack.push(value);

        int emptyStackTop = emptyStack.top();
        int stackTop = stack.top();

        // Assert
        assertThat(emptyStackTop, equalTo(value));
        assertThat(stackTop, equalTo(value));
REPOBEE-SANITIZER-END
    }
}
```

>Example 1: The simplest usage of `repobee-sanitizer` using a .java file

For this .java test file, the `santize-file` command will identify the START and END markers, and proceed to remove the code inbetween. The result will look like this:

```java
class StackTest {
    @Test
    public void topIsLastPushedValue() {
    }
}
```

`repobee-sanitizer` also supports the `REPOBEE-SANITIZER-REPLACE-WITH` marker. By adding a replace marker, we can specify code that should replace the removed code. Example as follows:

````java
class StackTest {
    @Test
    public void topIsLastPushedValue() {
REPOBEE-SANITIZER-START
        // Arrange
        int value = 1338;

        // Act
        emptyStack.push(value);
        stack.push(value);

        int emptyStackTop = emptyStack.top();
        int stackTop = stack.top();

        // Assert
        assertThat(emptyStackTop, equalTo(value));
        assertThat(stackTop, equalTo(value));
REPOBEE-SANITIZER-REPLACE-WITH
        fail("Not implemented");
REPOBEE-SANITIZER-END
    }
}
````

> Example 2: The code is the same as for example 1, but we have added a `REPOBEE-SANITIZER-REPLACE-WITH` marker.

As we can see in Example 2, this lets us provide two versions of a function, one that is current, and one that will replace it. Example 1 and 2 shows us a piece of code used in the KTH course DD1338. This code is part of an assignment where students are asked to implement a test function. The example shows a finished solution that is availiable to the teachers of the course. However, because of `repobee-sanitizer` and the `REPLACE-WITH` marker, the code can be reduced to the following:

````java
class StackTest {
    @Test
    public void topIsLastPushedValue() {
        fail("Not implemented");
    }
}
````

> Example 3: Sanitized code that is provided to students.

We can see that the only code that remains inside the function is that of the `REPLACE-WITH` marker. This gives us the main usage that `repobee-santizer` was developed for, it allows us to combine finished solutions with the "skeletonized" solutions that are provided to students.

# Prefixing

Sometimes (usually) we want code that can run, its a good thing then that `repobee-sanitizer` blocks can be commented out! Example 2 will produce the same output as the following:

````java
class StackTest {
    @Test
    public void topIsLastPushedValue() {
//REPOBEE-SANITIZER-START
        // Arrange
        int value = 1338;

        // Act
        emptyStack.push(value);
        stack.push(value);

        int emptyStackTop = emptyStack.top();
        int stackTop = stack.top();

        // Assert
        assertThat(emptyStackTop, equalTo(value));
        assertThat(stackTop, equalTo(value));
//REPOBEE-SANITIZER-REPLACE-WITH
//        fail("Not implemented");
//REPOBEE-SANITIZER-END
    }
}
````

> Example 4: Java code with `repobee-sanitizer` related syntax commented out

`repobee-sanitizer` automatically detects if there is a prefix in front of any markers. This way we can have java comments: `//`, python comments: `#` or similar preceding our markers. **This means code can still compile!**

## Some rules for prefixing:

`repobee-sanitizer`:

* Determines prefix as any text that comes before `REPOBEE-SANITIZER-START`
* Only determines prefix on a block-to-block basis, meaning that the prefix selected at a `BLOCK` marker must be used untill and including the next `END` marker
  * This means that all `repobee-sanitizer` blocks can have individuall prefixes
* Code between replace and end markers **MUST** also be prefixed

# Syntax

for `repobee-sanitizer` to work, marker syntax must be correct, this includes spelling of the markers themselves, the markers currently are as follows:

- REPOBEE-SANITIZER-START
    - REQUIRED: A block is not a block without a start marker
    - Indicates the start of a block. Any text will be removed untill reaching a `REPLACE-WITH` or `END` marker.
- REPOBEE-SANITIZER-REPLACE-WITH
    - OPTIONAL: but requires a start and end block.
    - Any text between this marker and the next `END` marker will remain.
- REPOBEE-SANITIZER-END
    - REQUIRED: Must exist for each start block
    - Indicates the end of a block.
- REPOBEE_SANITIZER-SHRED
    - OPTIONAL: Can only exist on the first line of a file. If this exists, there cannot be any other markers of any type in the file
    - Having this marker will remove the entire file when running the `sanitize-repo` or `sanitize-file` commands

If a marker is incorrectly spelled, `repobee-sanitizer` will report an error.

# License

See [LICENSE](LICENSE) for details.

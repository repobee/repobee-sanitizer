# repobee-sanitizer
A plugin for RepoBee to sanitize template repositories before being pushed to students. 
`repobee-sanitizer` adds the commands `sanitize-file` and `sanitize-repo` that lets the user sanitize files and repos (directories currently) respectively.
`repobee-sanitizer` can remove or replace text by going through files, looking for certain `REPOBEE-SANITIZER-<type>` text-markers. The most simple usage consists of a `REPOBEE-SANITIZER-BLOCK` and a `REPOBEE-SANITIZER-END` marker, where content between these two markers will be removes, or "santitized".

# Install

[WIP]

# Usage
`repobee-sanitizer` is currently under development, it currently supports the `sanitize-file` and `sanitize-repo` commands. Because `repobee-sanitizer` is a plugin to `repobee`, these commands are executed by running repobee with:

> repobee -p repobee-sanitizer sanitize-repo

(is this right?)

# Example use cases
Consider the following code:

```
class StackTest {
    @Test
    public void topIsLastPushedValue() {
REPOBEE-SANITIZER-BLOCK
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
>Example 1: For this .java test file, the `santize-file` command will identify the START and END markers, and proceed to remove the code inbetween.

`repobee-sanitizer` also supports the `REPOBEE-SANITIZER-REPLACE-WITH` marker. By adding a replace marker, we can specify code that should replace the removed code. Example as follows:

````
class StackTest {
    @Test
    public void topIsLastPushedValue() {
REPOBEE-SANITIZER-BLOCK
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

````
class StackTest {
    @Test
    public void topIsLastPushedValue() {
        fail("Not implemented");
    }
}
````

> Example 3: Skeletonized code that is provided to students.

We can see that the only code that remains inside the function is that of the `REPLACE-WITH` marker. This gives us the main usage that `repobee-santizer` was developed for, it allows us to combine finished solutions with the "skeletonized" solutions that are provided to students.

# Prefixing
Sometimes (usually) we want code that can run, its a good thing then that `repobee-sanitizer` blocks can be commented out! Example two will produce the same output as the following:

````
class StackTest {
    @Test
    public void topIsLastPushedValue() {
//REPOBEE-SANITIZER-BLOCK
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
* Determines prefix as any text that comes before `REPOBEE-SANITIZER-BLOCK`
* Only determines prefix on a block-to-block basis, meaning that the prefix selected at a `BLOCK` marker must be used untill and including the next `END` marker 
    * This means that all `repobee-sanitizer` blocks can have individuall prefixes


# Syntax
for `repobee-sanitizer` to work, marker syntax must be correct, this includes spelling of the markers themselves, the markers currently are as follows:

- REPOBEE-SANITIZER-BLOCK
    - REQUIRED: A block is not a block without a start marker
    - Indicates the start of a block. Any text will be removed untill reaching a `REPLACE-WITH` or `END` marker. 
- REPOBEE-SANITIZER-REPLACE-WITH
    - OPTIONAL: but requires a start and end block.
    - Any text between this marker and the next `END` marker will remain.
- REPOBEE-SANITIZER-END
    - REQUIRED: Must exist for each start block
    - Indicates the end of a block.

If a marker is incorrectly spelled, `repobee-sanitizer` will report an error. 

# License
See [LICENSE](LICENSE) for details.

# Terminology
Block
Marker
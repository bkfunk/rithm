# rithm
A language designed for processing, analyzing, and visualizing data.

`rithm` has a number of features designed to make working with data easier:
- dataframes (a.k.a. data tables) are a _first class data type_.
- _algorithms_ provide a way to describe multi-step processes that is both _boilerplate free_ and _easy to debug and adapt_.

## Primitive data types

- int (Integers)
- float
-

## Algorithms

Use the keyword `algo` to create a new algorithm. An algorithm is simply a process that has multiple _steps_, which are executed one after another. When working with data, you frequently need to do a lot of little procedures, which are often clunky to work with and hard to debug. `algo`s make this much easier.

For example, let's say you have a dataframe `df` and you want to:

1. Rename a few cryptically named variables
2. Convert column names to camel_case
3. Split a string column on `,`, and create two new columns from it (and delete the old column)

Here's how you would do that in Python using pandas:

```python
from rithm.examples import titanic

def clean_data(df):
    df.rename(columns={
        "Pclass": "passenger_class",
        "SibSp": "num_siblings_spouses",
        "Parch": "num_parents_children"
    }, inplace=True)
    df.columns = to_camel_case(df.columns)
    df[['last_name', 'first_name']] = df['name'].str.split(', ')
    df.drop(columns='name', inplace=True)
```

Then, I can call `clean_data(titanic)`
and change the `titanic` dataframe.

Now, what happens if the name splitting code is not behaving as you expect (for example, maybe some rows have zero commas, or more than one)? Well, what you want to do is get the result of the splitting line _before_ the original `name` column has been dropped, so you can inspect the inputs and the outputs and see what's going on. So, you need to comment out that last line (which drops the column), re-run the code, and then you can interact with the `titanic` dataframe.

With `algo`s in `rithm`, you can do this:

```rithm
algo clean_data(df) do
    df -rename-> do
        @Pclass as @passenger_class
        @SibSp as @num_siblings_spouses
        @Parch as @num_parents_children
        .columns => to_camel_case
    end
    -split_names-> do
        @name => split(", ")
        => to_columns(@last_name, @first_name)
    end
end
```

Now, to get the state of titanic 

`titanic -> clean_data@split_names#1st`

This will apply the `clean_data` algorithm to `titanic` _up until the 1st step of the `split_names` step_.

Use `->` to pipe an argument to a function
Use `=>` to _modify_ an argument in place
Use `as` to rename a variable or column.


# Open questions

1. Should we have implicit variable declaration, like Python? Or use `let`? Or `var`? `const`?

2. Should blocks return the last value in the block?

3. Should blocks always be do/end?

4. Should we return values from variable assignment?

5. Should we use Empty for None? Or is ? enough? Is there a difference between a null value and an unknown value?

6. How should the if condition be terminated? A `then` keyword? Or a `do` block? Either?

7. How to avoid or handle dangling else clause? use `endif`? or `end`?

8. Should and/or return the arguments, or True/False? Should `x = 0 or 10` be 10, or True?

9. Should we have a `new` keyword? Or create instances as Python does?

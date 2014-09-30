# Bootstrapify
Modifies some built-in templates to use markup based on Twitter Bootstrap conventions.

## Usage
To enable *Bootstrapify* you have to include its JavaScript code:

```HTML
<script type="text/javascript" src="candyshop/bootstrapify/candy.js"></script>
```

Call its `init()` method *before* Candy has been initialized:

```JavaScript

// enable Bootstrapify plugin
CandyShop.Bootstrapify.init();

Candy.init('/http-bind/');

Candy.Core.connect();
```

This may break other plugins that modify built-in templates.

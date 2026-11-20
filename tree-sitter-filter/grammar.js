/**
 * @file A filter language for admin queries
 * @author Najla Gianneta Agisny, Nida Atqiya
 * @license MIT
 */


module.exports = grammar({
  name: 'filter',
  extras: $ => [/\s/],
  rules: {
    query: $ => $.comparison,
    
    comparison: $ => seq(
      $.identifier,
      choice('=', '!=', '>', '<', '>=', '<='),
      choice($.string, $.number)
    ),

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_.]*/,
    string: $ => /"[^"]*"/,
    number: $ => /[0-9]+/,
  }
});

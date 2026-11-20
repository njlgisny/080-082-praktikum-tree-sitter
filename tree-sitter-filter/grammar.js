/**
 * @file A filter language for admin queries
 * @author Najla Gianneta Agisny, Nida Atqiya
 * @license MIT
 */


module.exports = grammar({
  name: 'filter',
  extras: $ => [/\s/],
  rules: {
    query: $ => $._expr,

    _expr: $ => $.comparison,

    comparison: $ => seq(
      $.identifier,
      choice('=', '!=', '>', '<', '>=', '<='),
      choice($.string, $.number)
    ),

    and_expression: $ => seq($._expr, 'and', $._expr),

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_.]*/,
    word: $ => $.identifier,
    string: $ => /"[^"]*"/,
    number: $ => /[0-9]+/,
  }
});

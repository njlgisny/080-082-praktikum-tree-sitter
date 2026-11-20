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

   _expr: $ => choice(
      $.comparison,
      $.and_expression,
      $.or_expression,
      $.parenthesized_expression,
      $.not_expression
    ),

    comparison: $ => seq(
      field('left', $.identifier),
      field('operator', choice('=', '!=', '>', '<', '>=', '<=', 'in', 'contains')),
      field('right', choice($.string, $.number, $.boolean, $.in_expression))
    ),

    and_expression: $ => prec.left(2, seq($._expr, 'and', $._expr)),

    or_expression: $ => prec.left(1, seq($._expr, 'or', $._expr)),

    parenthesized_expression: $ => seq('(', $._expr, ')'),

    not_expression: $ => prec(3, seq('not', $._expr)),

    boolean: $ => choice('true', 'false'),

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_.]*/,
    word: $ => $.identifier,
    string: $ => /"[^"]*"/,
    number: $ => /[0-9]+/,
  }
});

export const PRESETS = [
  {
    name: "Ends with 'ab'",
    description: "Accepts strings over {a,b} whose suffix is 'ab'",
    nfa: {
      states: ['q0', 'q1', 'q2'],
      alphabet: ['a', 'b'],
      transitions: {
        q0: { a: ['q0', 'q1'], b: ['q0'] },
        q1: { b: ['q2'] },
      },
      start_state: 'q0',
      accept_states: ['q2'],
    },
    testStrings: ['ab', 'aab', 'bab', 'ababab', 'a', 'b', 'ba'],
  },
  {
    name: 'a* | b+  (with ε)',
    description: 'Accepts zero-or-more a  OR  one-or-more b  via ε-NFA',
    nfa: {
      states: ['s', 'q0', 'q1', 'r0', 'r1'],
      alphabet: ['a', 'b'],
      transitions: {
        s:  { epsilon: ['q0', 'q1', 'r0'] },
        q0: { a: ['q1'] },
        q1: { a: ['q1'] },
        r0: { b: ['r1'] },
        r1: { b: ['r1'] },
      },
      start_state: 's',
      accept_states: ['q1', 'r1'],
    },
    testStrings: ['', 'a', 'aa', 'b', 'bb', 'ab', 'ba'],
  },
  {
    name: "Contains '101'",
    description: "Accepts binary strings containing the substring '101'",
    nfa: {
      states: ['q0', 'q1', 'q2', 'q3'],
      alphabet: ['0', '1'],
      transitions: {
        q0: { '0': ['q0'], '1': ['q0', 'q1'] },
        q1: { '0': ['q2'] },
        q2: { '1': ['q3'] },
        q3: { '0': ['q3'], '1': ['q3'] },
      },
      start_state: 'q0',
      accept_states: ['q3'],
    },
    testStrings: ['101', '1101', '10110', '100', '010', '111'],
  },
  {
    name: 'Divisible by 3 (unary)',
    description: 'Accepts unary numbers whose length is divisible by 3',
    nfa: {
      states: ['q0', 'q1', 'q2'],
      alphabet: ['1'],
      transitions: {
        q0: { '1': ['q1'] },
        q1: { '1': ['q2'] },
        q2: { '1': ['q0'] },
      },
      start_state: 'q0',
      accept_states: ['q0'],
    },
    testStrings: ['', '1', '11', '111', '111111', '1111'],
  },
]

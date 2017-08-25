var assert = require('chai').assert;
var dataTools = require('../application/static/javascripts/rd-data-tools');
var tableObjects = require('../application/static/javascripts/rd-table-objects');

describe('rd-table-objects', function() {
  describe('#buildTableObject()', function() {
    it('should return a simple table if no group column', function() {
      var tableWithNull = tableObjects.buildTableObject(getSimpleArrayData(),'title', '', '', 'Ethnicity', '', null, ['Value'], '', ['']);
      var tableWithEmpty = tableObjects.buildTableObject(getSimpleArrayData(),'title', '', '', 'Ethnicity', '', '', ['Value'], '', ['']);
      var tableWithNoneString = tableObjects.buildTableObject(getSimpleArrayData(),'title', '', '', 'Ethnicity', '', '[None]', ['Value'], '', ['']);
      assert.equal(tableWithNull.type, 'simple');
      assert.equal(tableWithEmpty.type, 'simple');
      assert.equal(tableWithNoneString.type, 'simple');
    });

    it('should return a grouped table if a group column is given', function() {
      var groupColumn = 'Socio-economic';
      var tableWithGroupColumn = tableObjects.buildTableObject(getGroupedArrayData(), 'title', '', '', 'Ethnicity', '', groupColumn, ['Value'], '', ['']);
      assert.equal(tableWithGroupColumn.type, 'grouped');
    });

    it('should accept null values for non-essential columns', function() {
      var table = tableObjects.buildTableObject(getSimpleArrayData(), null, null, null, 'Ethnicity', null, null, ['Value'], null, ['']);
      assert.isObject(table);
    });
  });

  describe('#simpleTable()', function() {
    it('should return an object', function() {
      var table = tableObjects.simpleTable(getSimpleArrayData(),'title', '', '', 'Ethnicity', '', ['Value'], '', ['']);
      assert.isObject(table);
    });

    it('should accept null values for non-essential columns', function() {
      var table = tableObjects.simpleTable(getSimpleArrayData(), null, null, null, 'Ethnicity', null, ['Value'], null, ['']);
      assert.isObject(table);
    });

    it('should accept null values for non-essential columns', function() {
      var table = tableObjects.simpleTable(getSimpleArrayData(), null, null, null, 'Ethnicity', null, ['Value'], null, null);
      assert.isObject(table);
    });
  });

  describe('#groupedTable()', function () {
    it('should return an object', function() {
      var table = tableObjects.groupedTable(getGroupedArrayData(),'title', '', '', 'Ethnicity', '', 'Socio-economic', ['Value'], '', ['']);
      assert.isObject(table);
    });

    it('should accept null values for non-essential columns', function() {
      var table = tableObjects.groupedTable(getGroupedArrayData(),null, null, null, 'Ethnicity', null, 'Socio-economic', ['Value'], null, null);
      assert.isObject(table);
    });

    it('should return rows sorted alphetically if null order specified', function() {
        var order_column = null;
        var table = tableObjects.groupedTable(getGroupedArrayData(),'title', '', '', 'Ethnicity', '', 'Socio-economic', ['Value'], order_column, ['']);

        assert.equal(table['data'][0]['category'], 'Any Other');
        assert.equal(table['data'][1]['category'], 'BAME');
        assert.equal(table['data'][2]['category'], 'White');
    });

    it('should return rows sorted by alternative column if specified', function() {
        var order_column = 'Alternate';
        var table = tableObjects.groupedTable(getGroupedArrayData(),'title', '', '', 'Ethnicity', '', 'Socio-economic', ['Value'], order_column, ['']);

        assert.equal(table['data'][0]['category'], 'White');
        assert.equal(table['data'][1]['category'], 'Any Other');
        assert.equal(table['data'][2]['category'], 'BAME');
    });

    it('should return rows in original order if [None] specified', function() {
        var order_column = '[None]';
        var table = tableObjects.groupedTable(getGroupedArrayData(),'title', '', '', 'Ethnicity', '', 'Socio-economic', ['Value'], order_column, ['']);

        assert.equal(table['data'][0]['category'], 'White');
        assert.equal(table['data'][1]['category'], 'BAME');
        assert.equal(table['data'][2]['category'], 'Any Other');
    });
  });
});

function getSimpleArrayData() {
  // These are all entirely fictitious numbers
  return  [
              ['Ethnicity',     'Value',   'Denominator'],
              ['White',         '10000',    '100020'    ],
              ['Black',         '15000',    '100030'    ],
              ['Mixed',         '5000',     '200020'    ],
              ['Asian',         '70000',    '200030'    ],
              ['Other',         '9000',     '300020'    ]
          ];
}

function getGroupedArrayData() {
  // These are all entirely fictitious numbers
  return [
            ['Ethnicity',     'Alternate',  'Socio-economic', 'Value',   'Denominator'],
            ['White',         '0',          'Rich',           '10000',    '100020'    ],
            ['White',         '0',          'Poor',           '5000',     '200020'    ],
            ['BAME',          '2',          'Rich',           '9000',     '300020'    ],
            ['BAME',          '2',          'Poor',           '4000',     '400020'    ],
            ['Any Other',     '1',          'Rich',           '9000',     '300020'    ],
            ['Any Other',     '1',          'Poor',           '4000',     '400020'    ]
         ];
}
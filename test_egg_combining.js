/**
 * Quick test for egg combining fix
 */

// Simulate the combiner logic
class TestCombiner {
  constructor() {
    this.ingredientFamilies = {
      'egg': ['egg', 'eggs', 'large eggs', 'medium eggs']
    };
  }
  
  normalizeUnit(unit, fullText = '') {
    if (!unit) return '';
    
    const lower = unit.toLowerCase();
    
    // These are all "count" units - normalize to empty string
    const countUnits = ['whole', 'count', 'piece', 'pieces', 'item', 'items'];
    if (countUnits.includes(lower)) {
      return '';
    }
    
    // Common adjectives that aren't units
    const adjectives = ['large', 'medium', 'small', 'fresh', 'dried', 'frozen', 
                        'raw', 'cooked', 'ripe', 'organic', 'free-range'];
    if (adjectives.includes(lower)) {
      return ''; // Skip adjectives, they're not units
    }
    
    // If the unit matches a known ingredient name, it's actually a count
    for (const [family, variations] of Object.entries(this.ingredientFamilies)) {
      if (variations.includes(lower) || family === lower) {
        return ''; // It's the ingredient itself, not a unit
      }
    }
    
    return lower;
  }
  
  extractQuantity(text) {
    const patterns = [
      /(\d+\.?\d*)\s*([a-zA-Z]+)/,
      /(\d+\/\d+)\s*([a-zA-Z]+)/,
      /(\d+)-(\d+)\s*([a-zA-Z]+)/,
      /(\d+\.?\d*)/
    ];
    
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        let amount;
        let unit = '';
        
        if (match[3]) {
          amount = (parseFloat(match[1]) + parseFloat(match[2])) / 2;
          unit = match[3];
        } else if (match[1].includes('/')) {
          const [num, den] = match[1].split('/').map(Number);
          amount = num / den;
          unit = match[2] || '';
        } else {
          amount = parseFloat(match[1]);
          unit = match[2] || '';
        }
        
        unit = this.normalizeUnit(unit.toLowerCase(), text.toLowerCase());
        return { amount, unit };
      }
    }
    
    return { amount: 1, unit: '' };
  }
  
  combineSimpleQuantities(quantities) {
    const byUnit = {};
    
    quantities.forEach(({ amount, unit }) => {
      if (!byUnit[unit]) byUnit[unit] = 0;
      byUnit[unit] += amount;
    });
    
    const units = Object.keys(byUnit);
    if (units.length === 1) {
      return { amount: byUnit[units[0]], unit: units[0] };
    }
    
    return null;
  }
}

// Test cases
console.log('🧪 Testing Egg Combining Fix\n');
console.log('='.repeat(60));

const combiner = new TestCombiner();

const testCases = [
  { name: '6 eggs', expected: { amount: 6, unit: '' } },
  { name: '12 eggs', expected: { amount: 12, unit: '' } },
  { name: 'eggs', expected: { amount: 1, unit: '' } },
  { name: '6 large eggs', expected: { amount: 6, unit: '' } },
  { name: '2 cups flour', expected: { amount: 2, unit: 'cups' } },
];

console.log('\n📝 Test 1: Quantity Extraction\n');
testCases.forEach(test => {
  const result = combiner.extractQuantity(test.name);
  const pass = result.amount === test.expected.amount && result.unit === test.expected.unit;
  console.log(`${pass ? '✅' : '❌'} "${test.name}"`);
  console.log(`   Expected: amount=${test.expected.amount}, unit="${test.expected.unit}"`);
  console.log(`   Got:      amount=${result.amount}, unit="${result.unit}"`);
});

console.log('\n📝 Test 2: Combining Eggs\n');
const eggQuantities = [
  combiner.extractQuantity('6 eggs'),
  combiner.extractQuantity('6 eggs')
];

console.log('Input quantities:');
eggQuantities.forEach(q => console.log(`  - amount: ${q.amount}, unit: "${q.unit}"`));

const combined = combiner.combineSimpleQuantities(eggQuantities);

console.log('\nCombined result:');
if (combined) {
  console.log(`  ✅ amount: ${combined.amount}, unit: "${combined.unit}"`);
  console.log(`  Display: "${combined.amount} eggs"`);
  
  if (combined.amount === 12 && combined.unit === '') {
    console.log('\n🎉 SUCCESS! Eggs combine correctly to "12 eggs"');
  } else {
    console.log('\n❌ FAILED! Expected 12 eggs');
  }
} else {
  console.log('  ❌ Failed to combine (returned null)');
}

console.log('\n' + '='.repeat(60));

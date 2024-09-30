import * as fuzzySearch from '@m31coding/fuzzy-search';
import fs from 'node:fs';

// better results than python lib used but still behind expected

const searcher = fuzzySearch.SearcherFactory.createDefaultSearcher();
let count = 0;

const readJsonlFileSync = (filePath) => {
  const data = fs.readFileSync(filePath, 'utf-8');
  return data.split('\n').filter(line => line.trim()).map(line => Object.assign(JSON.parse(line), { id: count++ }));
};

const answeredData = readJsonlFileSync('../../data/answeredQuestions.jsonl');
const unansweredData = readJsonlFileSync('../../data/unansweredTextLabels.jsonl').map((data) => ({id: data.id, question: data.Label}));

const indexingMeta = searcher.indexEntities(
  answeredData,
  (e) => e.id,
  (e) => [e.question, e.answer]
);


const questionsFinal = [];
for (const data of unansweredData) {
  const resultData = searcher.getMatches(new fuzzySearch.Query(data.question)).matches[0]
  if (resultData !== undefined) {
    if (resultData.quality > 0.6) {
      questionsFinal.push({expected: data.question, result: resultData.entity.question, taxa: resultData.quality});
    }
  }
    
}

console.dir(questionsFinal);
console.dir(questionsFinal.length);
console.dir(unansweredData.length);
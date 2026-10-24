import {createHash} from 'node:crypto';
import {writeFileSync} from 'node:fs';
const result=[];
for (const url of ['https://driftlock-nine.vercel.app/driftlock-test-covenant.txt','https://linktr.ee/Marymmm']) {
 const response=await fetch(url); const bytes=Buffer.from(await response.arrayBuffer());
 result.push({url,status:response.status,scope:'RAW_HTTP_RESPONSE_BODY_NOT_GENLAYER_RENDERED_TEXT',bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
 if(url.endsWith('.txt')) writeFileSync('.qa-live/restored-primary.txt',bytes);
}
writeFileSync('.qa-live/restored-source-hashes.json',JSON.stringify(result,null,2)); console.log(JSON.stringify(result,null,2));

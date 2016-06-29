import sys
import pandas as pd
import ultrajson as json
from helpers import haversine

act_path = sys.argv[1]
pred_path = sys.argv[2]
out_path = sys.argv[3]

print '-- loading actual locations --'
act = map(json.loads, open(act_path))
act = pd.DataFrame(act)
act.columns = ['act_' + c for c in act.columns]
act = act.drop_duplicates().reset_index(drop=True)

print '-- loading predicted locations --'
pred = map(json.loads, open(pred_path))
pred = pd.DataFrame(pred)
pred.columns = ['pred_' + c for c in pred.columns]
pred = pred.drop_duplicates().reset_index(drop=True)

print '-- merging --'
df = pd.merge(act, pred, left_on='act_source', right_on='pred_source')
df['dist'] = df.apply(lambda x: haversine((x['act_lat'], x['act_lon']), (x['pred_lat'], x['pred_lon'])), 1)

print '-- saving --'
df.to_csv(out_path)
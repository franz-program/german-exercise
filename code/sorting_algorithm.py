from random import uniform

def process_sorting_indexes(priorities, tries, errors):

    priorities = [int(p) for p in priorities]
    max_priority = max(priorities)
    priorities = [p/max_priority for p in priorities]
    points_for_priority = [uniform(p/3, max(10, 3*p)) + uniform(2, 5) if p > 0.8 else 0 for p in priorities]
    
    tries = [int(t) for t in tries]
    errors = [int(e) for e in errors]
    errors_ratios = [e/t if t > 0 else 0.5 for e, t in zip(errors, tries)]
    points_for_errors = [uniform(3, 5)*e if e > 0.2 else uniform(0,1)*e for e in errors_ratios]

    avg_tries = sum(tries)/len(tries) if sum(tries) > 0 else 1
    tries = [t/avg_tries for t in tries]
    points_for_tries = [uniform(2, 5)*t if t < 0.5 else uniform(1, 3)*t for t in tries]

    total_points = [p + e + t for p, e, t in zip(points_for_priority, points_for_errors, points_for_tries)]

    return [i[0] for i in sorted(enumerate(total_points), key=lambda x:x[1], reverse=True)]


    
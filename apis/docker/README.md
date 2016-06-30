### Docker Geoinference

The geoinference analytic has two components
	ginf-graph
		stores information about user locations and @mention graphs
	ginf-predict
		computes (or retrieves) average/predicted location for a given user

#### Quickstart 
	
	# Start graph service
	cd $PROJECT_ROOT/apis/docker/ginf-graph
	./copy-src.sh
	docker build -t ginf-graph .
	docker run -p 5000:5000 ginf-graph

	# Start predict service
	cd $PROJECT_ROOT/apis/docker/ginf-predict
	./copy-src.sh
	docker build -t ginf-predict .
	docker run -p 6000:6000 ginf-predict

	# Test
	cd $PROJECT_ROOT/apis/docker/tests
	
    ./test_graph.sh
    # Eventually returns
    # {
    #   "did-mention": "ginf:did-mention:2147874481", 
    #   "post-locations": "ginf:post-locations:2147874481", 
    #   "was-mentioned": [
    #     "ginf:was-mentioned:2253591092"
    #   ]
    # }
    
	./test_api.sh
    # {
    #   "mode": "actual", 
    #   "model": "ginf-predict-01", 
    #   "value": {
    #     "iter": 1.0, 
    #     "lat": -23.683, 
    #     "lon": -46.596, 
    #     "mad": 0.0, 
    #     "n": 153.0
    #   }
    # }

Both APIs take GNIP formatted tweets as input. See `tests/test_*.sh` for examples of interface.

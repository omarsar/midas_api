require 'net/http'
require 'cgi'
require 'csv'
require 'json'
require 'uri'
require 'mongo'
require 'set'
include Mongo

def post(payload)
	payload = payload.to_json
    uri = URI("http://192.168.2.30:8080/webresources/jammin/emotion")

     	req = Net::HTTP::Post.new(uri.path, initheader = {'Content-Type' =>'application/json'})
          
     
          req.body = payload
          response = Net::HTTP.new("192.168.2.30", 8080).start {|http| http.request(req) }
          
end






mongo_client = MongoClient.new("localhost", 27017)
insert_coll = mongo_client['patients']['bipolar_experts']
coll = mongo_client['idea']['bipolar_experts_polarity_clean']
#insert_coll = mongo_client['patients']['bb_mix']
#coll = mongo_client['idea']['bb_mix_polarity']


processed_tweets = Set.new

insert_coll.find do |cursor|
	cursor.each do |tweet|

		processed_tweets.add(tweet["id"])


	end


end

target_tweets = Set.new

coll.find({},:timeout => false) do |cursor|
        cursor.each do |tweet|

                target_tweets.add(tweet["id"])


        end


end



puts "processed_tweets length:#{processed_tweets.length}"
puts "target_tweets length:#{target_tweets.length}"


fail_count = 0

uri = URI("http://192.168.2.30:8080/webresources/jammin/emotion")
dataList = []

hit = 0
loop_count = 0 


coll.find({},:timeout => false) do |cursor|


repetation = 0
	cursor.each do |tweet|
		

               loop_count += 1
#		begin
		if not processed_tweets.include? tweet["id"]
			hit +=1		
			puts tweet["id"]			
			text = tweet['text'].strip()

			payload ={:text => text, :lang => "en"}
			

			requestData = post payload
      
        	

			if requestData.is_a?(Net::HTTPSuccess)
				emoHash =  JSON.parse(requestData.body)
				tweet["emotion"] = emoHash
				tweet.delete("_id")
				
				dataList.push(tweet)
				
					
			else
				puts "HTTP Failed"
				fail_count += 1 
		end
			
			end
			if dataList.length > 100
         		bulk = insert_coll.initialize_ordered_bulk_op

        		 dataList.each do |data|
                  	bulk.insert(data)
         		end
         		p bulk.execute
     			puts "Insert"
         		dataList = []
    		end




			
	#	rescue
			

#			puts $!
#			puts  $@
#		end
	end
end
puts hit 
puts loop_count
puts fail_count
bulk = insert_coll.initialize_ordered_bulk_op

 dataList.each do |data|
                        bulk.insert(data)
                        end
                        p bulk.execute
                        puts "Insert"


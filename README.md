START TRAINING

make training 
MODEL_NAME=DilleniaUPC     #ชื่อ file
START_MODEL=tha                   #ภาษาที่เลือกใช้ เช่น ไทย tha.traineddata
TESSDATA=../tessdata/              #ที่เก็บ tesseract tha.trained modelเริ่มต้น จาก tesseract lstm
MAX_ITERATIONS=6000           # รอบการ train
LEARNING_RATE=0.0005         # ค่า lr
เมื่อ train รอบแรกเสร็จจะได้

CONTINUE TRAINING

lstmtraining 
--continue_from data/DilleniaUPC/checkpoints/DilleniaUPC_17.066_5900_5900.checkpoint 
--traineddata data/DilleniaUPC/DilleniaUPC.traineddata 
--model_output data/DilleniaUPC/checkpoints/DilleniaUPC
--train_listfile data/DilleniaUPC/list.train 
--max_iterations 12000 
--learning_rate 0.0001

explain
--continue_from ตามด้วย path ที่เก็บ .checkpoint ที่เราค้องการ (ปกติเลือกต่อจากอันเดิม ล่าสุด)
--traineddata หลังจาก train รอบแรกจะได้ model มา 1 ตัวคือตัวนี้ นั่นคือตัวนี้
--model_output path ที่ออกของ model ตัวถัดไป
--train_listfile fileที่เก็บว่าล่าสุดเราใช้ data ตัวไหนไปแล้วบ้าง

adjust parameter อีกครั้ง ถ้าไม่ใส่จะทำไปเรื่อยๆ และได้เป็น checkpoint แทน
--max_iterations 12000 
--learning_rate 0.0001


OUTPUT MODEL WITH CHECKPOINT

lstmtraining 
--stop_training 
--continue_from data/DilleniaUPC/checkpoints/DilleniaUPC.traineddata_0.625_76028_153800.checkpoint --traineddata data/DilleniaUPC/DilleniaUPC.traineddata 
--model_output data/DilleniaUPC/DilleniaUPC_0.587_34_100(ชื่อoutput)

explain
--stop_training  	หยุด train
--continue_from  	ตามด้วย path เก็บ checkpoint
--traineddata model 	model ตัวล่าสุดที่ train เสร็จ
--model_output 	modelตัวใหม่ที่จะออกมา



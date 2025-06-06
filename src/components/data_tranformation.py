import sys 
import os
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder , StandardScaler

from src.exception import CustomeException
from src.logger import logging

from src.utils import save_object
from src.utils import save_object , evaluate_models


@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts', 'preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def get_data_transformer_object(self):
        '''

        This Function is Responsible for the data Transformation

        '''
        try:
            numerical_columns =['writing_score' , 'reading_score']
            categorical_columns = ['gender' , 
                                   'race_ethnicity' ,
                                    'parental_level_of_education' ,
                                    'lunch' , 
                                    'test_preparation_course']
            num_pipeline = Pipeline(
                steps=[
                    ("imputer",SimpleImputer(strategy='median')),
                     ('scaler' , StandardScaler())
            ])

            cat_pipeline = Pipeline(
                steps=[
                    ('imputer' , SimpleImputer(strategy='most_frequent')),
                    ('one_hot_encoder' , OneHotEncoder(sparse_output=False)),
                    ('scaler' , StandardScaler())
                ]
            )
            logging.info(f'Categorical columns :{categorical_columns}')

            logging.info(f'Numerical columns : {numerical_columns}')

            logging.info('Categorical columns encoding is completed ')

            preprocessor = ColumnTransformer(
                [
                    ('num_pipeline', num_pipeline , numerical_columns),
                    ('cat_pipeline' ,cat_pipeline , categorical_columns)
                ]
            )

            return preprocessor
        
        except Exception as e:
            raise CustomeException(e , sys)
        

    def initiate_data_transformation(self , train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info('Reading train and test data is completed ')
            logging.info('obtaining preprocessing Object')

            preprocessor_object = self.get_data_transformer_object()

            target_column_name = 'math_score'
            numerical_columns = ['writing_score' , 'reading_score']

            input_feature_train_df = train_df.drop(columns=[target_column_name] , axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name] , axis = 1)
            target_feature_test_df = test_df[target_column_name]

            logging.info(
                f'Applying Preprocessing Object on Training Dataframe and Testing Dataframe'
            )

            input_feature_train_arr = preprocessor_object.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessor_object.fit_transform(input_feature_test_df)


            train_arr = np.c_[
                input_feature_train_arr , np.array(target_feature_train_df)

            ]
            test_arr = np.c_[input_feature_test_arr , np.array(target_feature_test_df)]
            
            logging.info(f'Saved Preprocessing Object')
            save_object(
                
                file_path=self.data_transformation_config.preprocessor_obj_file_path , 
                obj= preprocessor_object 


            )

            return (
                train_arr,
                test_arr , 
                self.data_transformation_config.preprocessor_obj_file_path , 
            )
        except Exception as e:
            raise CustomeException(e , sys)
            

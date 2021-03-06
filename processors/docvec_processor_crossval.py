from sklearn import model_selection, linear_model, svm
from sklearn.metrics import make_scorer
from xgboost import XGBRegressor

from entities.semeval_tagged_line_document import SemevalTaggedLineDocument
from processors.processor import Processor
from utils import doc2vec_helper
from utils import file_helper
from utils import log_helper
from utils.evaluation_helper import evaluate_task_score

log = log_helper.get_logger("DocvecProcessorCrossval")


class DocvecProcessorCrossval(Processor):

    def process(self):
        log.info("Began Processing")

        semeval_train_docs = SemevalTaggedLineDocument(self.options.train_headlines_data_path)

        doc2vec_model = \
            doc2vec_helper.init_model(
                semeval_train_docs, self.options.docvec_dimension_size, self.options.docvec_iteration_count
            )
        log.info("Doc2vec model initialized with " + str(self.options.docvec_dimension_size) +
                 " dimensions and " + str(self.options.docvec_iteration_count) + " iterations")

        x_articles, y_train = file_helper.get_article_details(self.options.train_headlines_data_path)

        x_train = list()
        for article in x_articles:
            x_vector = doc2vec_model.infer_vector(article)
            x_train.append(x_vector)

        x_test_articles, y_true = file_helper.get_article_details(self.options.test_headlines_data_path)
        custom_scorer = make_scorer(evaluate_task_score)

        x_test = list()
        for article in x_test_articles:
            x_vector = doc2vec_model.infer_vector(article)
            x_test.append(x_vector)

        x_train.extend(x_test)
        y_train.extend(y_true)
        scores = model_selection.cross_val_score(svm.LinearSVR(), x_train,
                                                 y_train, cv=10, scoring=custom_scorer)

        log.info("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

        log.info("Completed Processing")

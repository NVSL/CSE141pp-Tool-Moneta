from moneta.model import Model
from moneta.view import View
from moneta.moneta_widgets import MonetaWidgets
from moneta.trace import Trace
from moneta.legend import Legend

class TestInit:
    def test_model(self):
        in_model = Model()
        assert hasattr(in_model, 'curr_trace')
        assert in_model.curr_trace is None

    def test_view(self):
        in_view = View(Model())
        assert hasattr(in_view, 'model')
        assert in_view.model is not None

    def test_moneta_widgets(self):
        in_mwidgets = MonetaWidgets()
        assert hasattr(in_mwidgets, 'cl')
        assert in_mwidgets.cl is not None

    def test_trace(self):
        name = ''
        in_trace = Trace('', '', '', '')
        assert hasattr(in_trace, 'name')
        assert hasattr(in_trace, 'err_message')
        assert in_trace.name == name

    def test_tag(self, mock_tags):
        in_tag = mock_tags[0]
        assert hasattr(in_tag, 'id_')
        assert type(in_tag.id_) is int

    def test_legend(self, mock_tags, mock_df):
        in_legend = Legend(mock_tags, mock_df)
        assert hasattr(in_legend, 'df')
        assert hasattr(in_legend, 'colormap')
        assert hasattr(in_legend, 'widgets')

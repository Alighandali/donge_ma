import streamlit as st
import copy

st.title("This is *Dong* Time :bar_chart:")
st.caption("'**Dong**' is a Farsi word for someone's share of a payment")


# Create objets in Streamlit cache
if 'attendee_keys' not in st.session_state:
    st.session_state.attendee_keys = []
if 'attendee_num' not in st.session_state:
    st.session_state.attendee_num = 0
if 'pay_keys' not in st.session_state:
    st.session_state.pay_keys = []
if 'pay_num' not in st.session_state:
    st.session_state.pay_num = 0
if 'attendee_objs' not in st.session_state:
    st.session_state.attendee_objs = []
if 'pay_objs' not in st.session_state:
    st.session_state.pay_objs = []
if 'calculated' not in st.session_state:
    st.session_state.calculated = 0


class Attendee:
    '''
    create object for an attendee
    '''
    def __init__(self, name):
        self.name = name
        self.must_receive = 0


pays_list = []


class Pay:
    '''
    create object for a payment
    '''
    def __init__(self, name, cost, buyer, users=[]):
        self.name = name
        self.cost = cost
        self.buyer = buyer
        self.users = users
        pays_list.append(self)

    def calculate(self):
        '''
        calculate share for each attendee
        '''
        res = {}
        self.list_users = self.users
        self.each_dong = self.cost / len(self.list_users)
        for person in self.list_users:
            person.must_receive -= self.each_dong
            res[person.name] = - self.each_dong
        self.buyer.must_receive += self.cost
        res[self.buyer.name] = res.get(self.buyer.name, 0) + self.cost
        self.each_dong = self.cost = 0
        return res


# receive and show attendees on sidebar
with st.sidebar:
    attendee_names = []
    if st.button("Add New Attendee :busts_in_silhouette:"):
        st.session_state.attendee_keys.append(st.session_state.attendee_num)
        person = Attendee(st.session_state.attendee_num)
        st.session_state.attendee_objs.append(person)
        st.session_state.attendee_num += 1
    for i in st.session_state.attendee_keys:
        attendee_name = st.text_input(
            f"{i + 1}th Attendee :bust_in_silhouette:",
            key=f"t{i}")
        st.session_state.attendee_objs[i].name = attendee_name
        attendee_names.append(attendee_name)

# receive and show pays
pay_names = []
if st.button("Add New Pay :moneybag:"):
    st.session_state.pay_keys.append(st.session_state.pay_num)
    pay = Pay(name=0, cost=0, buyer=0, users=[])
    st.session_state.pay_objs.append(pay)
    st.session_state.pay_num += 1
for i in st.session_state.pay_keys:
    with st.expander(f"**{i + 1}th Pay Detail** :memo:"):
        col11, col12, col13 = st.columns(3)
        with col11:
            pay_name = st.text_input(f"**{i + 1}th Pay** :heavy_dollar_sign:",
                                     key=f"p{i}", placeholder="Dinner")
        with col12:
            pay_cost = st.number_input(f"**{i + 1}th Cost** :credit_card:",
                                       key=f"c{i}", step=1000)
        with col13:
            buyer_name = st.selectbox(
                f"**{i + 1}th Buyer** :money_with_wings:",
                options=attendee_names, key=f"b{i}")
            for j, _ in enumerate(st.session_state.attendee_objs):
                if buyer_name == st.session_state.attendee_objs[j].name:
                    buyer_name = st.session_state.attendee_objs[j]
        users = st.multiselect("**Who Use It?** :yum:",
                               attendee_names, key=f"u{i}")
        for k, _ in enumerate(users):
            for n, _ in enumerate(st.session_state.attendee_objs):
                if users[k] == st.session_state.attendee_objs[n].name:
                    users[k] = st.session_state.attendee_objs[n]

        st.session_state.pay_objs[i].name = pay_name
        st.session_state.pay_objs[i].cost = pay_cost
        st.session_state.pay_objs[i].buyer = buyer_name
        st.session_state.pay_objs[i].users = users
        pay_names.append((pay_name, pay_cost))


def calculate_all():
    '''
    aggregate all pays and calculate the final shares
    '''
    if st.session_state.calculated == 0 or st.session_state.attendee_objs:
        for pay in st.session_state.pay_objs:
            pay.calculate()


def transactions(x_list):
    '''
    show all money transactions to be done
    '''
    y_list = copy.deepcopy(x_list)
    y_list.sort(key=lambda y_list: y_list[0])
    report = []
    while len(y_list) > 1:
        transaction = min(abs(y_list[0][0]), abs(y_list[-1][0]))
        y_list[0][0] += transaction
        y_list[-1][0] -= transaction
        report.append(
            f":red[**{y_list[0][1].title()}**] **{transaction}**\
                  :point_right: :green[**{y_list[-1][1].title()}**]")
        if abs(y_list[0][0]) < abs(y_list[-1][0]):
            y_list.pop(0)
        else:
            y_list.pop(-1)
    return report


# show the final result
st.divider()
col1, col2, col3 = st.columns(3)
with col3:
    if st.button("Calculate :abacus:", type="primary"):
        if len(st.session_state.attendee_objs) != 0:
            for person in st.session_state.attendee_objs:
                person.must_receive = 0
            calculate_all()
            with col1:
                st.subheader("Each attendee:")
                total_res = {}
                for person in st.session_state.attendee_objs:
                    total_res[person.name] = person.must_receive
                    if person.must_receive > 0:
                        color = 'green'
                        emoji = ':thumbsup:'
                    else:
                        color = 'red'
                        emoji = ':thumbsdown:'
                    st.markdown(f"**{person.name.title():<10}:**\
                                :{color}[**{person.must_receive:,}** {emoji}]")
            with col2:
                st.subheader("Transactions:")
                total_list = []
                for i, person in enumerate(st.session_state.attendee_objs):
                    total_list.append([person.must_receive, person.name])
                transactions_res = transactions(total_list)
                for trans in transactions_res:
                    st.markdown(trans)

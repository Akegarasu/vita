package top.ghang.springbootstatemachine.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;
import org.springframework.statemachine.config.EnableStateMachine;
import org.springframework.statemachine.config.EnumStateMachineConfigurerAdapter;
import org.springframework.statemachine.config.builders.StateMachineStateConfigurer;
import org.springframework.statemachine.config.builders.StateMachineTransitionConfigurer;
import top.ghang.springbootstatemachine.enums.Events;
import top.ghang.springbootstatemachine.enums.States;

import java.util.EnumSet;

@Configuration
@EnableStateMachine
public class StateMachineConfig extends EnumStateMachineConfigurerAdapter<States, Events> {

    private Logger logger = LoggerFactory.getLogger(getClass());

    // 状态机状态配置
    @Override
    public void configure(StateMachineStateConfigurer<States, Events> states) throws Exception {
        // 定义状态机中的状态
        states.withStates().initial(States.UNPAID) // 初始状态
                .states(EnumSet.allOf(States.class));
    }

    // 状态机转换配置
    @Override
    public void configure(StateMachineTransitionConfigurer<States, Events> transitions) throws Exception {
        transitions
                .withExternal()
                    .source(States.UNPAID).target(States.WAITING_FOR_RECEIVE)
                    .event(Events.PAY) // 指定状态来源和目标
                    .and() // 指定触发事件
                .withExternal()
                    .source(States.WAITING_FOR_RECEIVE).target(States.DONE)
                    .event(Events.RECEIVE);
    }

    //@Override
    //public void configure(StateMachineConfigurationConfigurer<States, Events> config) throws Exception {
    //    config
    //            .withConfiguration()
    //                .listener(listener());  // 指定状态机的处理监听器
    //}

    //@Bean
    //public StateMachineListener<States, Events> listener() {
    //    return new StateMachineListenerAdapter<States, Events>() {
    //        @Override
    //        public void transition(Transition<States, Events> transition) {
    //            if (transition.getTarget().getId() == States.UNPAID) {
    //                logger.info("订单创建，待支付");
    //                return;
    //            }
    //
    //            if (transition.getSource().getId() == States.UNPAID && transition.getTarget().getId() == States.WAITING_FOR_RECEIVE) {
    //                logger.info("用户完成支付，待收货");
    //                return;
    //            }
    //
    //            if (transition.getSource().getId() == States.WAITING_FOR_RECEIVE && transition.getTarget().getId() == States.DONE) {
    //                logger.info("用户已收货，订单完成");
    //                return;
    //            }
    //        }
    //    };
    //}
}
